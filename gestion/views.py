from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone

from coopeV3.acl import active_required, acl_or

import simplejson as json
from dal import autocomplete
from decimal import *

from .forms import ReloadForm, RefundForm, ProductForm, KegForm, MenuForm, GestionForm, SearchMenuForm, SearchProductForm, SelectPositiveKegForm, SelectActiveKegForm
from .models import Product, Menu, Keg, ConsumptionHistory, KegHistory, Consumption, MenuHistory
from preferences.models import PaymentMethod

@active_required
@login_required
@acl_or('gestion.add_consumptionhistory', 'gestion.add_reload', 'gestion.add_refund')
def manage(request):
    pay_buttons = PaymentMethod.objects.filter(is_active=True)
    gestion_form = GestionForm(request.POST or None)
    reload_form = ReloadForm(request.POST or None)
    refund_form = RefundForm(request.POST or None)
    bieresPression = []
    bieresBouteille = Product.objects.filter(category=Product.BOTTLE).filter(is_active=True)
    panini = Product.objects.filter(category=Product.PANINI).filter(is_active=True)
    food = Product.objects.filter(category=Product.FOOD).filter(is_active=True)
    soft = Product.objects.filter(category=Product.SOFT).filter(is_active=True)
    menus = Menu.objects.filter(is_active=True)
    kegs = Keg.objects.filter(is_active=True)
    for keg in kegs:
        if(keg.pinte):
            bieresPression.append(keg.pinte)
        if(keg.demi):
            bieresPression.append(keg.demi)
        if(keg.galopin):
            bieresPression.append(keg.galopin)
    return render(request, "gestion/manage.html", {"gestion_form": gestion_form, "reload_form": reload_form, "refund_form": refund_form, "bieresPression": bieresPression, "bieresBouteille": bieresBouteille, "panini": panini, "food": food, "soft": soft, "menus": menus, "pay_buttons": pay_buttons})

@login_required
@permission_required('gestion.add_consumptionhistory')
@csrf_exempt
def order(request):
    if("user" not in request.POST or "paymentMethod" not in request.POST or "amount" not in request.POST or "order" not in request.POST):
        return HttpResponse("Erreur du POST")
    else:
        user = get_object_or_404(User, pk=request.POST['user'])
        paymentMethod = get_object_or_404(PaymentMethod, pk=request.POST['paymentMethod'])
        amount = Decimal(request.POST['amount'])
        order = json.loads(request.POST["order"])
        menus = json.loads(request.POST["menus"])
        if (not order) and (not menus):
            return HttpResponse("Pas de commande")
        adherentRequired = False
        for o in order:
            product = get_object_or_404(Product, pk=o["pk"])
            adherentRequired = adherentRequired or product.adherentRequired
        for m in menus:
            menu = get_object_or_404(Menu, pk=m["pk"])
            adherentRequired = adherentRequired or menu.adherent_required
        if(adherentRequired and not user.profile.is_adherent):
            return HttpResponse("N'est pas adhérent et devrait l'être")
        if(paymentMethod.affect_balance):
            if(user.profile.balance < amount):
                return HttpResponse("Solde inférieur au prix de la commande")
            else:
                user.profile.debit += amount
                user.save()
        for o in order:
            product = get_object_or_404(Product, pk=o["pk"])
            quantity = int(o["quantity"])
            if(product.category == Product.P_PRESSION):
                keg = get_object_or_404(Keg, pinte=product)
                if(not keg.is_active):
                    return HttpResponse("Une erreur inconnue s'est produite. Veuillez contacter le trésorier ou le président")
                kegHistory = get_object_or_404(KegHistory, keg=keg, isCurrentKegHistory=True)
                kegHistory.quantitySold += Decimal(quantity * 0.5)
                kegHistory.amountSold += Decimal(quantity * product.amount)
                kegHistory.save()
            elif(product.category == Product.D_PRESSION):
                keg = get_object_or_404(Keg, demi=product)
                if(not keg.is_active):
                    return HttpResponse("Une erreur inconnue s'est produite. Veuillez contacter le trésorier ou le président")
                kegHistory = get_object_or_404(KegHistory, keg=keg, isCurrentKegHistory=True)
                kegHistory.quantitySold += Decimal(quantity * 0.25)
                kegHistory.amountSold += Decimal(quantity * product.amount)
                kegHistory.save()
            elif(product.category == Product.G_PRESSION):
                keg = get_object_or_404(Keg, galopin=product)
                if(not keg.is_active):
                    return HttpResponse("Une erreur inconnue s'est produite. Veuillez contacter le trésorier ou le président")
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
            ch = ConsumptionHistory(customer = user, quantity = quantity, paymentMethod=paymentMethod, product=product, amount=int(quantity*product.amount), coopeman=request.user)
            ch.save()
        for m in menus:
            menu = get_object_or_404(Menu, pk=m["pk"])
            quantity = int(m["quantity"])
            mh = MenuHistory(customer=user, quantity=quantity, paymentMethod=paymentMethod, menu=menu, amount=int(quantity*menu.amount), coopeman=request.user)
            mh.save()
            for article in menu.articles.all():
                consumption, _ = Consumption.objects.get_or_create(customer=user, product=article)
                consumption.quantity += quantity
                consumption.save()
                if(article.stockHold > 0):
                    article.stockHold -= 1
                    article.save()
        return HttpResponse("La commande a bien été effectuée")

@login_required
@permission_required('gestion.add_reload')
def reload(request):
    reload_form = ReloadForm(request.POST or None)
    if(reload_form.is_valid()):
        reloadEntry = reload_form.save(commit=False)
        reloadEntry.coopeman = request.user
        reloadEntry.save()
        user = reload_form.cleaned_data['customer']
        amount = reload_form.cleaned_data['amount']
        user.profile.credit += amount
        user.save()
        messages.success(request,"Le compte de " + user.username + " a bien été crédité de " + str(amount) + "€")
    else:
        messages.error(request, "Le rechargement a échoué")
    return redirect(reverse('gestion:manage'))

@login_required
@permission_required('gestion.add_refund')
def refund(request):
    refund_form = RefundForm(request.POST or None)
    if(refund_form.is_valid()):
        user = refund_form.cleaned_data['customer']
        amount = refund_form.cleaned_data['amount']
        if(amount <= user.profile.balance):
            refundEntry = refund_form.save(commit = False)
            refundEntry.coopeman = request.user
            refundEntry.save()
            user.profile.credit -= amount
            user.save()
            messages.success(request, "Le compte de " + user.username + " a bien été remboursé de " + str(amount) + "€")
        else:
            messages.error(request, "Impossible de rembourser l'utilisateur " + user.username + " de " + str(amount)  + "€ : il n'a que " + str(user.profile.balance)  + "€ sur son compte.")
    else:
        messages.error(request, "Le remboursement a échoué")
    return redirect(reverse('gestion:manage'))

@login_required
@permission_required('gestion.delete_consumptionhistory')
def cancel_consumption(request, pk):
    consumption = get_object_or_404(ConsumptionHistory, pk=pk)
    user = consumption.customer
    user.profile.debit -= consumption.amount
    user.save()
    consumption.delete()
    messages.success(request, "La consommation a bien été annulée")
    return redirect(reverse('users:profile', kwargs={'pk': user.pk}))

@login_required
@permission_required('gestion.delete_menuhistory')
def cancel_menu(request, pk):
    menu_history = get_object_or_404(MenuHistory, pk=pk)
    user = menu_history.customer
    user.profile.debit -= menu_history.amount
    user.save()
    menu_history.delete()
    messages.success(request, "La consommation du menu a bien été annulée")
    return redirect(reverse('users:profile', kwargs={'pk': user.pk}))

########## Products ##########

@login_required
@acl_or('gestion.add_product', 'gestion.view_product', 'gestion.add_keg', 'gestion.view_keg', 'gestion.change_keg', 'gestion.view_menu', 'gestion.add_menu')
def productsIndex(request):
    return render(request, "gestion/products_index.html")

@login_required
@permission_required('gestion.add_product')
def addProduct(request):
    form = ProductForm(request.POST or None)
    if(form.is_valid()):
        form.save()
        messages.success(request, "Le produit a bien été ajouté")
        return redirect(reverse('gestion:productsList'))
    return render(request, "form.html", {"form": form, "form_title": "Ajout d'un produit", "form_button": "Ajouter"})

@login_required
@permission_required('gestion.edit_product')
def editProduct(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if(form.is_valid()):
        form.save()
        messages.success(request, "Le produit a bien été modifié")
        return redirect(reverse('gestion:productsList'))
    return render(request, "form.html", {"form": form, "form_title": "Modification d'un produit", "form_button": "Modifier"})

@login_required
@permission_required('gestion.view_product')
def productsList(request):
    products = Product.objects.all()
    return render(request, "gestion/products_list.html", {"products": products})

@login_required
@permission_required('gestion.view_product')
def searchProduct(request):
    form = SearchProductForm(request.POST or None)
    if(form.is_valid()):
        return redirect(reverse('gestion:productProfile', kwargs={'pk': form.cleaned_data['product'].pk }))
    return render(request, "form.html", {"form": form, "form_title":"Rechercher un produit", "form_button": "Rechercher"})

@login_required
@permission_required('gestion.view_product')
def productProfile(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "gestion/product_profile.html", {"product": product})
  
@login_required
def getProduct(request, barcode):
    product = Product.objects.get(barcode=barcode)
    data = json.dumps({"pk": product.pk, "barcode" : product.barcode, "name": product.name, "amount" : product.amount})
    return HttpResponse(data, content_type='application/json')

@login_required
@permission_required('gestion.edit_product')
def switch_activate(request, pk):
    """
    If the product is active, switch to not active.
    If the product is not active, switch to active.
    """
    product = get_object_or_404(Product, pk=pk)
    product.is_active = 1 - product.is_active
    product.save()
    messages.success(request, "La disponibilité du produit a bien été changée")
    return redirect(reverse('gestion:productsList'))

class ProductsAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Product.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs

########## Kegs ##########

@login_required
@permission_required('gestion.add_keg')
def addKeg(request):
    form = KegForm(request.POST or None)
    if(form.is_valid()):
        keg = form.save()
        messages.success(request, "Le fût " + keg.name + " a bien été ajouté")
        return redirect(reverse('gestion:kegsList'))
    return render(request, "form.html", {"form":form, "form_title": "Ajout d'un fût", "form_button": "Ajouter"})

@login_required
@permission_required('gestion.edit_keg')
def editKeg(request, pk):
    keg = get_object_or_404(Keg, pk=pk)
    form = KegForm(request.POST or None, instance=keg)
    if(form.is_valid()):
        form.save()
        messages.success(request, "Le fût a bien été modifié")
        return redirect(reverse('gestion:kegsList'))
    return render(request, "form.html", {"form": form, "form_title": "Modification d'un fût", "form_button": "Modifier"})

@login_required
@permission_required('gestion.open_keg')
def openKeg(request):
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
    return render(request, "form.html", {"form": form, "form_title":"Percutage d'un fût", "form_button":"Percuter"})

@login_required
@permission_required('gestion.open_keg')
def openDirectKeg(request, pk):
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

@login_required
@permission_required('gestion.close_keg')
def closeKeg(request):
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
    return render(request, "form.html", {"form": form, "form_title":"Fermeture d'un fût", "form_button":"Fermer le fût"})

@login_required
@permission_required('gestion:close_keg')
def closeDirectKeg(request, pk):
    keg = get_object_or_404(Keg, pk=pk)
    if(keg.is_active):
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

@login_required
@permission_required('gestion.view_keg')
def kegsList(request):
    kegs_active = KegHistory.objects.filter(isCurrentKegHistory=True)
    ids_actives = kegs_active.values('id')
    kegs_inactive = Keg.objects.exclude(id__in = ids_actives)
    return render(request, "gestion/kegs_list.html", {"kegs_active": kegs_active, "kegs_inactive": kegs_inactive})

@login_required
@permission_required('gestion.view_keghistory')
def kegH(request, pk):
    keg = get_object_or_404(Keg, pk=pk)
    kegHistory = KegHistory.objects.filter(keg=keg).order_by('-openingDate')
    return render(request, "gestion/kegh.html", {"keg": keg, "kegHistory": kegHistory})

class KegActiveAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Keg.objects.filter(is_active = True)
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs

class KegPositiveAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Keg.objects.filter(stockHold__gt = 0)
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs

########## Menus ##########

@login_required
@permission_required('gestion.add_menu')
def addMenu(request):
    form = MenuForm(request.POST or None)
    extra_css = "#id_articles{height:200px;}"
    if(form.is_valid()):
        menu = form.save()
        messages.success(request, "Le menu " + menu.name + " a bien été ajouté")
        return redirect(reverse('gestion:menusList'))
    return render(request, "form.html", {"form":form, "form_title": "Ajout d'un menu", "form_button": "Ajouter", "extra_css": extra_css})

@login_required
@permission_required('gestion.edit_menu')
def edit_menu(request, pk):
    menu = get_object_or_404(Menu, pk=pk)
    form = MenuForm(request.POST or None, instance=menu)
    extra_css = "#id_articles{height:200px;}"
    if form.is_valid():
        form.save()
        messages.success(request, "Le menu a bien été modifié")
        return redirect(reverse('gestion:menusList'))
    return render(request, "form.html", {"form": form, "form_title": "Modification d'un menu", "form_button": "Modifier", "extra_css": extra_css})

@login_required
@permission_required('gestion.view_menu')
def searchMenu(request):
    """
    Search a menu via SearchMenuForm instance

    **Context**

    ``form_entete``
        The form title.

    ``form``
        The SearchMenuForm instance.

    ``form_button``
        The content of the form button.

    **Template**

    :template:`form.html`
    """
    form = SearchMenuForm(request.POST or None)
    if(form.is_valid()):
        menu = form.cleaned_data['menu']
        return redirect(reverse('gestion:editMenu', kwargs={'pk':menu.pk}))
    return render(request, "form.html", {"form": form, "form_title": "Recherche d'un menu", "form_button": "Modifier"})

@login_required
@permission_required('gestion.view_menu')
def menus_list(request):
    menus = Menu.objects.all()
    return render(request, "gestion/menus_list.html", {"menus": menus})

@login_required
@permission_required('gestion.edit_menu')
def switch_activate_menu(request, pk):
    """
    If the menu is active, switch to not active.
    If the menu is not active, switch to active.
    """
    menu = get_object_or_404(Menu, pk=pk)
    menu.is_active = 1 - menu.is_active
    menu.save()
    messages.success(request, "La disponibilité du menu a bien été changée")
    return redirect(reverse('gestion:menusList'))

@login_required
def get_menu(request, barcode):
    menu = get_object_or_404(Menu, barcode=barcode)
    data = json.dumps({"pk": menu.pk, "barcode" : menu.barcode, "name": menu.name, "amount" : menu.amount})
    return HttpResponse(data, content_type='application/json')

class MenusAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Menu.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs
########## Ranking ##########

@login_required
def ranking(request):
    bestBuyers = User.objects.order_by('-profile__debit')[:25]
    customers = User.objects.all()
    list = []
    for customer in customers:
        alcohol = customer.profile.alcohol
        list.append([customer, alcohol])
    bestDrinkers = sorted(list, key=lambda x: x[1], reverse=True)[:25]
    return render(request, "gestion/ranking.html", {"bestBuyers": bestBuyers, "bestDrinkers": bestDrinkers})

@login_required
def annualRanking(request):
    return render(request, "gestion/annual_ranking.html")
