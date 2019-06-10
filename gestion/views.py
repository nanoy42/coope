from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.db import transaction

from datetime import datetime, timedelta

from django_tex.views import render_to_pdf
from coopeV3.acl import active_required, acl_or, admin_required

import simplejson as json
from dal import autocomplete
from decimal import *

from .forms import ReloadForm, RefundForm, ProductForm, KegForm, MenuForm, GestionForm, SearchMenuForm, SearchProductForm, SelectPositiveKegForm, SelectActiveKegForm, PinteForm, GenerateReleveForm, CategoryForm, SearchCategoryForm
from .models import Product, Menu, Keg, ConsumptionHistory, KegHistory, Consumption, MenuHistory, Pinte, Reload, Refund, Category
from users.models import School
from preferences.models import PaymentMethod, GeneralPreferences, Cotisation
from users.models import CotisationHistory

@active_required
@login_required
@acl_or('gestion.add_consumptionhistory', 'gestion.add_reload', 'gestion.add_refund')
def manage(request):
    """
    Displays the manage view.
    """
    categories = Category.objects.exclude(order=0).order_by('order')
    pay_buttons = PaymentMethod.objects.filter(is_active=True)
    gestion_form = GestionForm(request.POST or None)
    reload_form = ReloadForm(request.POST or None)
    refund_form = RefundForm(request.POST or None)
    bieresPression = []
    menus = Menu.objects.filter(is_active=True)
    kegs = Keg.objects.filter(is_active=True)
    gp, _ = GeneralPreferences.objects.get_or_create(pk=1)
    cotisations = Cotisation.objects.all()
    floating_buttons = gp.floating_buttons
    for keg in kegs:
        if(keg.pinte):
            bieresPression.append(keg.pinte)
        if(keg.demi):
            bieresPression.append(keg.demi)
        if(keg.galopin):
            bieresPression.append(keg.galopin)
    return render(request, "gestion/manage.html", {
        "gestion_form": gestion_form,
        "reload_form": reload_form,
        "refund_form": refund_form,
        "bieresPression": bieresPression,
        "categories": categories,
        "pay_buttons": pay_buttons,
        "floating_buttons": floating_buttons,
        "cotisations": cotisations
        })

@csrf_exempt
@active_required
@login_required
@permission_required('gestion.add_consumptionhistory')
def order(request):
    """
    Processes the given order. The order is passed through POST.
    """
    error_message = "Impossible d'effectuer la transaction. Toute opération abandonnée. Veuillez contacter le président ou le trésorier"
    try:
        with transaction.atomic():
            if("user" not in request.POST or "paymentMethod" not in request.POST or "amount" not in request.POST or "order" not in request.POST):
                raise Exception("Erreur du post")
            else:
                user = get_object_or_404(User, pk=request.POST['user'])
                paymentMethod = get_object_or_404(PaymentMethod, pk=request.POST['paymentMethod'])
                amount = Decimal(request.POST['amount'])
                order = json.loads(request.POST["order"])
                menus = json.loads(request.POST["menus"])
                listPintes = json.loads(request.POST["listPintes"])
                cotisations = json.loads(request.POST['cotisations'])
                gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
                if (not order) and (not menus) and (not cotisations):
                    error_message = "Pas de commande"
                    raise Exception(error_message)
                if(cotisations):
                    for co in cotisations:
                        cotisation = Cotisation.objects.get(pk=co['pk'])
                        for i in range(co['quantity']):
                            cotisation_history = CotisationHistory(cotisation=cotisation)
                            if(paymentMethod.affect_balance):
                                if(user.profile.balance >= cotisation_history.cotisation.amount):
                                    user.profile.debit += cotisation_history.cotisation.amount
                                else:
                                    error_message = "Solde insuffisant"
                                    raise Exception(error_message)
                            cotisation_history.user = user
                            cotisation_history.coopeman = request.user
                            cotisation_history.amount = cotisation.amount
                            cotisation_history.duration = cotisation.duration
                            cotisation_history.paymentMethod = paymentMethod
                            if(user.profile.cotisationEnd and user.profile.cotisationEnd > timezone.now()):
                                cotisation_history.endDate = user.profile.cotisationEnd + timedelta(days=cotisation.duration)
                            else:
                                cotisation_history.endDate = timezone.now() + timedelta(days=cotisation.duration)
                            user.profile.cotisationEnd = cotisation_history.endDate
                            user.save()
                            cotisation_history.save()
                adherentRequired = False
                for o in order:
                    product = get_object_or_404(Product, pk=o["pk"])
                    adherentRequired = adherentRequired or product.adherentRequired
                for m in menus:
                    menu = get_object_or_404(Menu, pk=m["pk"])
                    adherentRequired = adherentRequired or menu.adherent_required
                if(adherentRequired and not user.profile.is_adherent):
                    error_message = "N'est pas adhérent et devrait l'être."
                    raise Exception(error_message)
                # Partie un peu complexe : je libère toutes les pintes de la commande, puis je test
                # s'il a trop de pintes non rendues, puis je réalloue les pintes
                for pinte in listPintes:
                    allocate(pinte, None)
                if(gp.use_pinte_monitoring and gp.lost_pintes_allowed and user.profile.nb_pintes >= gp.lost_pintes_allowed):
                    error_message = "Impossible de réaliser la commande : l'utilisateur a perdu trop de pintes."
                    raise Exception(error_message)
                for pinte in listPintes:
                    allocate(pinte, user)
                for o in order:
                    product = get_object_or_404(Product, pk=o["pk"])
                    quantity = int(o["quantity"])
                    if(product.draft_category == Product.DRAFT_PINTE):
                        keg = get_object_or_404(Keg, pinte=product)
                        if(not keg.is_active):
                            raise Exception("Fût non actif")
                        kegHistory = get_object_or_404(KegHistory, keg=keg, isCurrentKegHistory=True)
                        kegHistory.quantitySold += Decimal(quantity * 0.5)
                        kegHistory.amountSold += Decimal(quantity * product.amount)
                        kegHistory.save()
                    elif(product.draft_category == Product.DRAFT_DEMI):
                        keg = get_object_or_404(Keg, demi=product)
                        if(not keg.is_active):
                            raise Exception("Fût non actif")
                        kegHistory = get_object_or_404(KegHistory, keg=keg, isCurrentKegHistory=True)
                        kegHistory.quantitySold += Decimal(quantity * 0.25)
                        kegHistory.amountSold += Decimal(quantity * product.amount)
                        kegHistory.save()
                    elif(product.draft_category == Product.DRAFT_GALOPIN):
                        keg = get_object_or_404(Keg, galopin=product)
                        if(not keg.is_active):
                            raise Exception("Fût non actif")
                        kegHistory = get_object_or_404(KegHistory, keg=keg, isCurrentKegHistory=True)
                        kegHistory.quantitySold += Decimal(quantity * 0.125)
                        kegHistory.amountSold += Decimal(quantity * product.amount)
                        kegHistory.save()
                    else:
                        if(product.stockHold > 0):
                            product.stockHold -= 1
                            product.save()
                    consumption, _ = Consumption.objects.get_or_create(customer=user, product=product)
                    consumption.quantity += quantity
                    consumption.save()
                    ch = ConsumptionHistory(customer=user, quantity=quantity, paymentMethod=paymentMethod, product=product, amount=Decimal(quantity*product.amount), coopeman=request.user)
                    ch.save()
                    if(paymentMethod.affect_balance):
                        if(user.profile.balance >= Decimal(product.amount*quantity)):
                            user.profile.debit += Decimal(product.amount*quantity)
                        else:
                            error_message = "Solde insuffisant"
                            raise Exception(error_message)
                for m in menus:
                    menu = get_object_or_404(Menu, pk=m["pk"])
                    quantity = int(m["quantity"])
                    mh = MenuHistory(customer=user, quantity=quantity, paymentMethod=paymentMethod, menu=menu, amount=int(quantity*menu.amount), coopeman=request.user)
                    mh.save()
                    if(paymentMethod.affect_balance):
                        if(user.profile.balance >= Decimal(product.amount*quantity)):
                            user.profile.debit += Decimal(product.amount*quantity)
                        else:
                            error_message = "Solde insuffisant"
                            raise Exception(error_message)
                    for article in menu.articles.all():
                        consumption, _ = Consumption.objects.get_or_create(customer=user, product=article)
                        consumption.quantity += quantity
                        consumption.save()
                        if(article.stockHold > 0):
                            article.stockHold -= 1
                            article.save()
                user.save()
                return HttpResponse("La commande a bien été effectuée")
    except Exception as e:
        print(e)
        print("test")
        return HttpResponse(error_message)

@active_required
@login_required
@permission_required('gestion.add_reload')
def reload(request):
    """
    Displays a :class:`Reload form <gestion.forms.reloadForm>`.
    """
    reload_form = ReloadForm(request.POST or None)
    if reload_form.is_valid():
        reload_entry = reload_form.save(commit=False)
        reload_entry.coopeman = request.user
        reload_entry.save()
        user = reload_form.cleaned_data['customer']
        amount = reload_form.cleaned_data['amount']
        user.profile.credit += amount
        user.save()
        messages.success(request, "Le compte de " + user.username + " a bien été crédité de " + str(amount) + "€")
    else:
        messages.error(request, "Le rechargement a échoué")
    return redirect(reverse('gestion:manage'))

@active_required
@login_required
@permission_required('gestion.delete_reload')
def cancel_reload(request, pk):
    """
    Delete a :class:`gestion.models.Reload`.

    pk
        The primary key of the reload to delete.
    """
    reload_entry = get_object_or_404(Reload, pk=pk)
    if reload_entry.customer.profile.balance >= reload_entry.amount:
        reload_entry.customer.profile.credit -= reload_entry.amount
        reload_entry.customer.save()
        reload_entry.delete()
        messages.success(request, "Le rechargement a bien été annulé.")
    else:
        messages.error(request, "Impossible d'annuler le rechargement. Le solde deviendrait négatif.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@active_required
@login_required
@permission_required('gestion.add_refund')
def refund(request):
    """
    Displays a :class:`Refund form <gestion.forms.RefundForm>`.
    """
    refund_form = RefundForm(request.POST or None)
    if refund_form.is_valid():
        user = refund_form.cleaned_data['customer']
        amount = refund_form.cleaned_data['amount']
        if amount <= user.profile.balance:
            refund_entry = refund_form.save(commit = False)
            refund_entry.coopeman = request.user
            refund_entry.save()
            user.profile.credit -= amount
            user.save()
            messages.success(request, "Le compte de " + user.username + " a bien été remboursé de " + str(amount) + "€")
        else:
            messages.error(request, "Impossible de rembourser l'utilisateur " + user.username + " de " + str(amount)  + "€ : il n'a que " + str(user.profile.balance)  + "€ sur son compte.")
    else:
        messages.error(request, "Le remboursement a échoué")
    return redirect(reverse('gestion:manage'))

@active_required
@login_required
@permission_required('gestion.delete_consumptionhistory')
def cancel_consumption(request, pk):
    """
    Delete a :class:`consumption history <gestion.models.ConsumptionHistory>`.

    pk
        The primary key of the consumption history to delete. 
    """
    consumption = get_object_or_404(ConsumptionHistory, pk=pk)
    user = consumption.customer
    if consumption.paymentMethod.affect_balance:
        user.profile.debit -= consumption.amount
        user.save()
    consumptionT = Consumption.objects.get(customer=user, product=consumption.product)
    consumptionT.quantity -= consumption.quantity
    consumptionT.save()
    consumption.delete()
    messages.success(request, "La consommation a bien été annulée")
    return redirect(reverse('users:profile', kwargs={'pk': user.pk}))

@active_required
@login_required
@permission_required('gestion.delete_menuhistory')
def cancel_menu(request, pk):
    """
    Delete a :class:`menu history <gestion.models.MenuHistory>`.

    pk
        The primary key of the menu history to delete. 
    """
    menu_history = get_object_or_404(MenuHistory, pk=pk)
    user = menu_history.customer
    if menu_history.paymentMethod.affect_balance:
        user.profile.debit -= menu_history.amount
        user.save()
    for product in manu_history.menu.articles:
        consumptionT = Consumption.objects.get(customer=user, product=product)
        consumptionT -= menu_history.quantity
        consumptionT.save()
    menu_history.delete()
    messages.success(request, "La consommation du menu a bien été annulée")
    return redirect(reverse('users:profile', kwargs={'pk': user.pk}))

########## Products ##########
@active_required
@login_required
@acl_or('gestion.add_product', 'gestion.view_product', 'gestion.add_keg', 'gestion.view_keg', 'gestion.change_keg', 'gestion.view_menu', 'gestion.add_menu')
def productsIndex(request):
    """
    Displays the products manage static page.
    """
    return render(request, "gestion/products_index.html")

@active_required
@login_required
@permission_required('gestion.add_product')
def addProduct(request):
    """
    Displays a :class:`gestion.forms.ProductForm` to add a product.
    """
    form = ProductForm(request.POST or None)
    if(form.is_valid()):
        product = form.save()
        messages.success(request, "Le produit a bien été ajouté")
        return redirect(reverse('gestion:productProfile', kwargs={'pk':product.pk}))
    return render(request, "form.html", {"form": form, "form_title": "Ajout d'un produit", "form_button": "Ajouter", "form_button_icon": "plus-square"})

@active_required
@login_required
@permission_required('gestion.change_product')
def editProduct(request, pk):
    """
    Displays a :class:`gestion.forms.ProductForm` to edit a product.

    pk
        The primary key of the the :class:`gestion.models.Product` to edit.
    """
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if(form.is_valid()):
        form.save()
        messages.success(request, "Le produit a bien été modifié")
        return redirect(reverse('gestion:productProfile', kwargs={'pk':product.pk}))
    return render(request, "form.html", {"form": form, "form_title": "Modification d'un produit", "form_button": "Modifier", "form_button_icon": "pencil-alt"})

@active_required
@login_required
@permission_required('gestion.view_product')
def productsList(request):
    """
    Display the list of :class:`products <gestion.models.Product>`.
    """
    products = Product.objects.all()
    return render(request, "gestion/products_list.html", {"products": products})

@active_required
@login_required
@permission_required('gestion.view_product')
def searchProduct(request):
    """
    Displays a :class:`gestion.forms.SearchProduct` to search a :class:`gestion.models.Product`.
    """
    form = SearchProductForm(request.POST or None)
    if(form.is_valid()):
        return redirect(reverse('gestion:productProfile', kwargs={'pk': form.cleaned_data['product'].pk }))
    return render(request, "form.html", {"form": form, "form_title":"Rechercher un produit", "form_button": "Rechercher", "form_button_icon": "search"})

@active_required
@login_required
@permission_required('gestion.view_product')
def productProfile(request, pk):
    """
    Displays the profile of a :class:`gestion.models.Product`.

    pk
        The primary key of the :class:`gestion.models.Product` to display profile.
    """
    product = get_object_or_404(Product, pk=pk)
    return render(request, "gestion/product_profile.html", {"product": product})

@active_required
@login_required
def getProduct(request, pk):
    """
    Get a :class:`gestion.models.Product` by barcode and return it in JSON format.

    pk
        The primary key of the :class:`gestion.models.Product` to get infos.
    """
    product = Product.objects.get(pk=pk)
    if product.category == Product.DRAFT_PINTE:
        nb_pintes = 1
    else:
        nb_pintes = 0
    data = json.dumps({"pk": product.pk, "barcode" : product.barcode, "name": product.name, "amount": product.amount, "needQuantityButton": product.needQuantityButton, "nb_pintes": nb_pintes})
    return HttpResponse(data, content_type='application/json')

@active_required
@login_required
@permission_required('gestion.change_product')
def switch_activate(request, pk):
    """
    Switch the active status of the requested :class:`gestion.models.Product`.

    pk
        The primary key of the :class:`gestion.models.Product` to display profile.
    """
    product = get_object_or_404(Product, pk=pk)
    product.is_active = 1 - product.is_active
    product.save()
    messages.success(request, "La disponibilité du produit a bien été changée")
    return redirect(reverse('gestion:productProfile', kwargs={'pk': product.pk}))

class ProductsAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete view for all :class:`products <gestion.models.Product>`.
    """
    def get_queryset(self):
        qs = Product.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

class ActiveProductsAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete view for active :class:`products <gestion.models.Product>`.
    """
    def get_queryset(self):
        qs = Product.objects.filter(is_active=True)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

########## Kegs ##########

@active_required
@login_required
@permission_required('gestion.add_keg')
def addKeg(request):
    """
    Displays a :class:`gestion.forms.KegForm` to add a :class:`gestion.models.Keg`.
    """
    form = KegForm(request.POST or None)
    if(form.is_valid()):
        keg = form.save()
        messages.success(request, "Le fût " + keg.name + " a bien été ajouté")
        return redirect(reverse('gestion:kegsList'))
    return render(request, "form.html", {"form":form, "form_title": "Ajout d'un fût", "form_button": "Ajouter", "form_button_icon": "plus-square"})

@active_required
@login_required
@permission_required('gestion.change_keg')
def editKeg(request, pk):
    """
    Displays a :class:`gestion.forms.KegForm` to edit a :class:`gestion.models.Keg`.

    pk
        The primary key of the :class:`gestion.models.Keg` to edit.
    """
    keg = get_object_or_404(Keg, pk=pk)
    form = KegForm(request.POST or None, instance=keg)
    if(form.is_valid()):
        form.save()
        messages.success(request, "Le fût a bien été modifié")
        return redirect(reverse('gestion:kegsList'))
    return render(request, "form.html", {"form": form, "form_title": "Modification d'un fût", "form_button": "Modifier", "form_button_icon": "pencil-alt"})

@active_required
@login_required
@permission_required('gestion.open_keg')
def openKeg(request):
    """
    Displays a :class:`gestion.forms.SelectPositiveKegForm` to open a :class:`gestion.models.Keg`.
    """
    form = SelectPositiveKegForm(request.POST or None)
    if(form.is_valid()):
        keg = form.cleaned_data['keg']
        previousKegHistory = KegHistory.objects.filter(keg=keg).filter(isCurrentKegHistory=True)
        for pkh in previousKegHistory:
            pkh.isCurrentKegHistory = False
            pkh.closingDate = timezone.now()
            pkh.save()
        kegHistory = KegHistory(keg = keg)
        kegHistory.save()
        keg.stockHold -= 1
        keg.is_active = True
        keg.save()
        messages.success(request, "Le fut a bien été percuté")
        return redirect(reverse('gestion:kegsList'))
    return render(request, "form.html", {"form": form, "form_title":"Percutage d'un fût", "form_button":"Percuter", "form_button_icon": "fill-drip"})

@active_required
@login_required
@permission_required('gestion.open_keg')
def openDirectKeg(request, pk):
    """
    Opens a class:`gestion.models.Keg`.

    pk
        The primary key of the class:`gestion.models.Keg` to open.
    """
    keg = get_object_or_404(Keg, pk=pk)
    if(keg.stockHold > 0):
        previousKegHistory = KegHistory.objects.filter(keg=keg).filter(isCurrentKegHistory=True)
        for pkh in previousKegHistory:
            pkh.isCurrentKegHistory = False
            pkh.closingDate = timezone.now()
            pkh.save()
        kegHistory = KegHistory(keg = keg)
        kegHistory.save()
        keg.stockHold -= 1
        keg.is_active = True
        keg.save()
        messages.success(request, "Le fût a bien été percuté")
    else:
        messages.error(request, "Il n'y a pas de fût en stock")
    return redirect(reverse('gestion:kegsList'))

@active_required
@login_required
@permission_required('gestion.close_keg')
def closeKeg(request):
    """
    Displays a :class:`gestion.forms.SelectPositiveKegForm` to open a :class:`gestion.models.Keg`.
    """
    form = SelectActiveKegForm(request.POST or None)
    if(form.is_valid()):
        keg = form.cleaned_data['keg']
        kegHistory = get_object_or_404(KegHistory, keg=keg, isCurrentKegHistory=True)
        kegHistory.isCurrentKegHistory = False
        kegHistory.closingDate = timezone.now()
        kegHistory.save()
        keg.is_active = False
        keg.save()
        messages.success(request, "Le fût a bien été fermé")
        return redirect(reverse('gestion:kegsList'))
    return render(request, "form.html", {"form": form, "form_title":"Fermeture d'un fût", "form_button":"Fermer le fût", "form_button_icon": "fill"})

@active_required
@login_required
@permission_required('gestion.close_keg')
def closeDirectKeg(request, pk):
    """
    Closes a class:`gestion.models.Keg`.

    pk
        The primary key of the class:`gestion.models.Keg` to open.
    """
    keg = get_object_or_404(Keg, pk=pk)
    if keg.is_active:
        kegHistory = get_object_or_404(KegHistory, keg=keg, isCurrentKegHistory=True)
        kegHistory.isCurrentKegHistory = False
        kegHistory.closingDate = timezone.now()
        kegHistory.save()
        keg.is_active = False
        keg.save()
        messages.success(request, "Le fût a bien été fermé")
    else:
        messages.error(request, "Le fût n'est pas ouvert")
    return redirect(reverse('gestion:kegsList'))

@active_required
@login_required
@permission_required('gestion.view_keg')
def kegsList(request):
    """
    Display the list of :class:`kegs <gestion.models.Keg>`.
    """
    kegs_active = KegHistory.objects.filter(isCurrentKegHistory=True)
    ids_actives = kegs_active.values('keg__id')
    kegs_inactive = Keg.objects.exclude(id__in = ids_actives)
    return render(request, "gestion/kegs_list.html", {"kegs_active": kegs_active, "kegs_inactive": kegs_inactive})

@active_required
@login_required
@permission_required('gestion.view_keghistory')
def kegH(request, pk):
    """
    Display the :class:`history <gestion.models.KegHistory>` of requested :class:`gestion.models.Keg`.
    """
    keg = get_object_or_404(Keg, pk=pk)
    kegHistory = KegHistory.objects.filter(keg=keg).order_by('-openingDate')
    return render(request, "gestion/kegh.html", {"keg": keg, "kegHistory": kegHistory})

class KegActiveAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete view for active :class:`kegs <gestion.models.Keg>`.
    """
    def get_queryset(self):
        qs = Keg.objects.filter(is_active = True)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

class KegPositiveAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete view for :class:`kegs <gestion.models.Keg>` with positive stockHold.
    """
    def get_queryset(self):
        qs = Keg.objects.filter(stockHold__gt = 0)
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

########## Menus ##########

@active_required
@login_required
@permission_required('gestion.add_menu')
def addMenu(request):
    """
    Display a :class:`gestion.forms.MenuForm` to add a :class:`gestion.models.Menu`.
    """
    form = MenuForm(request.POST or None)
    extra_css = "#id_articles{height:200px;}"
    if(form.is_valid()):
        menu = form.save()
        messages.success(request, "Le menu " + menu.name + " a bien été ajouté")
        return redirect(reverse('gestion:menusList'))
    return render(request, "form.html", {"form":form, "form_title": "Ajout d'un menu", "form_button": "Ajouter", "form_button_icon": "plus-square", "extra_css": extra_css})

@active_required
@login_required
@permission_required('gestion.change_menu')
def edit_menu(request, pk):
    """
    Displays a :class:`gestion.forms.MenuForm` to edit a :class:`gestion.models.Menu`.

    pk
        The primary key of the :class:`gestion.models.Menu` to edit.
    """
    menu = get_object_or_404(Menu, pk=pk)
    form = MenuForm(request.POST or None, instance=menu)
    extra_css = "#id_articles{height:200px;}"
    if form.is_valid():
        form.save()
        messages.success(request, "Le menu a bien été modifié")
        return redirect(reverse('gestion:menusList'))
    return render(request, "form.html", {"form": form, "form_title": "Modification d'un menu", "form_button": "Modifier", "form_button_icon": "pencil-alt", "extra_css": extra_css})

@active_required
@login_required
@permission_required('gestion.view_menu')
def searchMenu(request):
    """
    Displays a :class:`gestion.forms.SearchMenuForm` to search a :class:`gestion.models.Menu`.
    """
    form = SearchMenuForm(request.POST or None)
    if(form.is_valid()):
        menu = form.cleaned_data['menu']
        return redirect(reverse('gestion:editMenu', kwargs={'pk':menu.pk}))
    return render(request, "form.html", {"form": form, "form_title": "Recherche d'un menu", "form_button": "Modifier", "form_button_icon": "search"})

@active_required
@login_required
@permission_required('gestion.view_menu')
def menus_list(request):
    """
    Display the list of :class:`menus <gestion.models.Menu>`.
    """
    menus = Menu.objects.all()
    return render(request, "gestion/menus_list.html", {"menus": menus})

@active_required
@login_required
@permission_required('gestion.change_menu')
def switch_activate_menu(request, pk):
    """
    Switch active status of a :class:`gestion.models.Menu`.
    """
    menu = get_object_or_404(Menu, pk=pk)
    menu.is_active = 1 - menu.is_active
    menu.save()
    messages.success(request, "La disponibilité du menu a bien été changée")
    return redirect(reverse('gestion:menusList'))

@active_required
@login_required
@permission_required('gestion.view_menu')
def get_menu(request, pk):
    """
    Get a :class:`gestion.models.Menu` by pk and return it in JSON format.

    pk
        The primary key of the :class:`gestion.models.Menu`.
    """
    menu = get_object_or_404(Menu, pk=pk)
    nb_pintes = 0
    for article in menu.articles:
        if article.category == Product.DRAFT_PINTE:
            nb_pintes +=1
    data = json.dumps({"pk": menu.pk, "barcode" : menu.barcode, "name": menu.name, "amount" : menu.amount, "needQuantityButton": False, "nb_pintes": nb_pintes})
    return HttpResponse(data, content_type='application/json')

class MenusAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete view for active :class:`menus <gestion.models.Menu>`.
    """
    def get_queryset(self):
        qs = Menu.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

########## Ranking ##########

@active_required
@login_required
def ranking(request):
    """
    Displays the ranking page.
    """
    bestBuyers = User.objects.order_by('-profile__debit')[:25]
    #customers = User.objects.all()
    #list = []
    #for customer in customers:
    #    alcohol = customer.profile.alcohol
    #    list.append([customer, alcohol])
    #bestDrinkers = sorted(list, key=lambda x: x[1], reverse=True)[:25]
    bestDrinkers = User.objects.order_by('-profile__alcohol')[:25]
    form = SearchProductForm(request.POST or None)
    if(form.is_valid()):
        product_ranking = form.cleaned_data['product'].ranking
    else:
        product_ranking = None
    return render(request, "gestion/ranking.html", {"bestBuyers": bestBuyers, "bestDrinkers": bestDrinkers, "product_ranking": product_ranking, "form": form})

########## Pinte monitoring ##########

def allocate(pinte_pk, user):
    """
    Allocate a :class:`gestion.models.Pinte` to a user (:class:`django.contrib.auth.models.User`) or release the pinte if user is None
    """
    try:
        pinte = Pinte.objects.get(pk=pinte_pk)
        if pinte.current_owner is not None:
            pinte.previous_owner = pinte.current_owner
        pinte.current_owner = user
        pinte.save()
        return True
    except Pinte.DoesNotExist:
        return False

@active_required
@login_required
@permission_required('gestion.change_pinte')
def release(request, pinte_pk):
    """
    View to release a :class:`gestion.models.Pinte`.

    pinte_pk
        The primary key of the :class:`gestion.models.Pinte` to release.
    """
    if allocate(pinte_pk, None):
        messages.success(request, "La pinte a bien été libérée")
    else:
        messages.error(request, "Impossible de libérer la pinte")
    return redirect(reverse('gestion:pintesList'))

@active_required
@login_required
@permission_required('gestion.add_pinte')
def add_pintes(request):
    """
    Displays a :class:`gestion.forms.PinteForm` to add one or more :class:`gestion.models.Pinte`.
    """
    form = PinteForm(request.POST or None)
    if form.is_valid():
        ids = form.cleaned_data['ids']
        if ids != "":
            ids = ids.split(" ")
        else:
            ids = range(form.cleaned_data['begin'], form.cleaned_data['end'] + 1)
        i = 0
        for id in ids:
            if not Pinte.objects.filter(pk=id).exists():
                new_pinte = Pinte(pk=int(id))
                new_pinte.save()
                i += 1
        messages.success(request, str(i) + " pinte(s) a(ont) été ajoutée(s)")
        return redirect(reverse('gestion:productsIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Ajouter des pintes", "form_button": "Ajouter", "form_button_icon": "plus-square"})

@active_required
@login_required
@permission_required('gestion.change_pinte')
def release_pintes(request):
    """
    Displays a :class:`gestion.forms.PinteForm` to release one or more :class:`gestion.models.Pinte`.
    """
    form = PinteForm(request.POST or None)
    if form.is_valid():
        ids = form.cleaned_data['ids']
        if ids != "":
            ids = ids.split(" ")
        else:
            ids = range(form.cleaned_data['begin'], form.cleaned_data['end'] + 1)
        i = 0
        for id in ids:
            if allocate(id, None):
                i += 1
        messages.success(request, str(i) + " pinte(s) a(ont) été libérée(s)")
        return redirect(reverse('gestion:productsIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Libérer des pintes", "form_button": "Libérer", "form_button_icon": "glass-whiskey"})

@active_required
@login_required
@permission_required('gestion.view_pinte')
def pintes_list(request):
    """
    Displays the list of :class:`gestion.models.Pinte`
    """
    free_pintes = Pinte.objects.filter(current_owner=None)
    taken_pintes = Pinte.objects.exclude(current_owner=None)
    return render(request, "gestion/pintes_list.html", {"free_pintes": free_pintes, "taken_pintes": taken_pintes})

@active_required
@login_required
@permission_required('auth.view_user')
def pintes_user_list(request):
    """
    Displays the list of user, who have unreturned :class:`Pinte(s) <gestion.models.Pinte>`.
    """
    pks = [x.pk for x in User.objects.all() if x.profile.nb_pintes > 0]
    users = User.objects.filter(pk__in=pks)
    return render(request, "gestion/pintes_user_list.html", {"users": users})

@active_required
@login_required
@admin_required
def gen_releve(request):
    """
    Displays a :class:`forms.gestion.GenerateReleveForm` to generate a releve.
    """
    form = GenerateReleveForm(request.POST or None)
    if form.is_valid():
        begin, end = form.cleaned_data['begin'], form.cleaned_data['end']
        consumptions = ConsumptionHistory.objects.filter(date__gte=begin).filter(date__lte=end).order_by('-date')
        reloads = Reload.objects.filter(date__gt=begin).filter(date__lt=end).order_by('-date')
        refunds = Refund.objects.filter(date__gt=begin).filter(date__lt=end).order_by('-date')
        cotisations = CotisationHistory.objects.filter(paymentDate__gt=begin).filter(paymentDate__lt=end).order_by('-paymentDate')
        especes = PaymentMethod.objects.get(name="Espèces")
        lydia = PaymentMethod.objects.get(name="Lydia")
        cheque = PaymentMethod.objects.get(name="Chèque")
        value_especes = 0
        value_lydia = 0
        value_cheque = 0
        for consumption in consumptions:
            pm = consumption.paymentMethod
            if pm == especes:
                value_especes += consumption.amount
            elif pm == lydia:
                value_lydia += consumption.amount
            elif pm == cheque:
                value_cheque += consumption.amount
        for reload in reloads:
            pm = reload.PaymentMethod
            if pm == especes:
                value_especes += reload.amount
            elif pm == lydia:
                value_lydia += reload.amount
            elif pm == cheque:
                value_cheque += reload.amount
        for refund in refunds:
            value_especes -= refund.amount
        for cot in cotisations:
            pm = cot.paymentMethod
            if pm == especes:
                value_especes += cot.amount
            elif pm == lydia:
                value_lydia += cot.amount
            elif pm == cheque:
                value_cheque += cot.amount
        now = datetime.now()
        return render_to_pdf(request, 'gestion/releve.tex', {"consumptions": consumptions, "reloads": reloads, "refunds": refunds, "cotisations": cotisations, "begin": begin, "end": end, "now": now, "value_especes": value_especes, "value_lydia": value_lydia, "value_cheque": value_cheque}, filename="releve.pdf")
    else:
        return render(request, "form.html", {"form": form, "form_title": "Génération d'un relevé", "form_button": "Générer", "form_button_icon": "file-pdf"})


########## categories ##########
@active_required
@login_required
@permission_required('gestion.add_category')
def addCategory(request):
    """
    Displays a :class:`gestion.forms.CategoryForm` to add a category.
    """
    form = CategoryForm(request.POST or None)
    if(form.is_valid()):
        category = form.save()
        messages.success(request, "La catégorie a bien été ajoutée")
        return redirect(reverse('gestion:categoryProfile', kwargs={'pk':category.pk}))
    return render(request, "form.html", {"form": form, "form_title": "Ajout d'une catégorie", "form_button": "Ajouter", "form_button_icon": "plus-square"})

@active_required
@login_required
@permission_required('gestion.change_category')
def editCategory(request, pk):
    """
    Displays a :class:`gestion.forms.CategoryForm` to edit a category.

    pk
        The primary key of the the :class:`gestion.models.Category` to edit.
    """
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if(form.is_valid()):
        form.save()
        messages.success(request, "La catégorie a bien été modifiée")
        return redirect(reverse('gestion:categoryProfile', kwargs={'pk': category.pk}))
    return render(request, "form.html", {"form": form, "form_title": "Modification d'une catégorie", "form_button": "Modifier", "form_button_icon": "pencil-alt"})

@active_required
@login_required
@permission_required('gestion.view_category')
def categoriesList(request):
    """
    Display the list of :class:`categories <gestion.models.Category>`.
    """
    categories = Category.objects.all().order_by('order')
    return render(request, "gestion/categories_list.html", {"categories": categories})

@active_required
@login_required
@permission_required('gestion.view_category')
def searchCategory(request):
    """
    Displays a :class:`gestion.forms.SearchCategory` to search a :class:`gestion.models.Category`.
    """
    form = SearchCategoryForm(request.POST or None)
    if(form.is_valid()):
        return redirect(reverse('gestion:categoryProfile', kwargs={'pk': form.cleaned_data['category'].pk }))
    return render(request, "form.html", {"form": form, "form_title":"Rechercher une catégorie", "form_button": "Rechercher", "form_button_icon": "search"})

@active_required
@login_required
@permission_required('gestion.view_category')
def categoryProfile(request, pk):
    """
    Displays the profile of a :class:`gestion.models.Category`.

    pk
        The primary key of the :class:`gestion.models.Category` to display profile.
    """
    category = get_object_or_404(Category, pk=pk)
    return render(request, "gestion/category_profile.html", {"category": category})

class CategoriesAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete view for active :class:`categories <gestion.models.Category>`.
    """
    def get_queryset(self):
        qs = Category.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs

@active_required
@login_required
@admin_required
def stats(request):
    users = User.objects.all()
    adherents = [x for x in users if x.profile.is_adherent]
    transactions = ConsumptionHistory.objects.all()
    categories = Category.objects.all()
    categories_shown = Category.objects.exclude(order=0)
    products = Product.objects.all()
    active_products = Product.objects.filter(is_active=True)
    active_kegs = Keg.objects.filter(is_active=True)
    sum_positive_balance = sum([x.profile.balance for x in users if x.profile.balance > 0])
    sum_balance = sum([x.profile.balance for x in users])
    schools = School.objects.all()
    groups = Group.objects.all()
    admins = User.objects.filter(is_staff=True)
    superusers = User.objects.filter(is_superuser=True)
    menus = Menu.objects.all()
    payment_methods = PaymentMethod.objects.all()
    cotisations = Cotisation.objects.all()
    return render(request, "gestion/stats.html", {
        "users": users,
        "adherents": adherents,
        "transactions": transactions,
        "categories": categories,
        "categories_shown": categories_shown,
        "products": products,
        "active_products": active_products,
        "active_kegs": active_kegs,
        "sum_positive_balance": sum_positive_balance,
        "sum_balance": sum_balance,
        "schools": schools,
        "groups": groups,
        "admins": admins,
        "superusers": superusers,
        "menus": menus,
        "payment_methods": payment_methods,
        "cotisations": cotisations,
    })