from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.http import HttpResponseRedirect

from coopeV3.acl import active_required, acl_or

import simplejson as json
from dal import autocomplete
from decimal import *

from .forms import ReloadForm, RefundForm, ProductForm, KegForm, MenuForm, GestionForm, SearchMenuForm, SearchProductForm, SelectPositiveKegForm, SelectActiveKegForm, PinteForm
from .models import Product, Menu, Keg, ConsumptionHistory, KegHistory, Consumption, MenuHistory, Pinte, Reload
from preferences.models import PaymentMethod, GeneralPreferences

@active_required
@login_required
@acl_or('gestion.add_consumptionhistory', 'gestion.add_reload', 'gestion.add_refund')
def manage(request):
    """
    Display the manage page

    **Context**
    
    ``gestion_form``
        The manage form
    
    ``reload_form``
        The :model:`gestion.Reload` form

    ``refund_form``
        The :model:`gestion.Refund` form

    ``bieresPression``
        A list of active :model:`gestion.Product` corresponding to draft beers

    ``bieresBouteille``
        A list of active :model:`gestion.Product` corresponding to bottle beers

    ``panini``
        A list of active :model:`gestion.Product` corresponding to panini items
        
    ``food``
        A list of active :model:`gestion.Product` corresponding to non-panini items

    ``soft``
        A list of active :model:`gestion.Product` correspond to non alcoholic beverage
    
    ``menus``
        The list of active :model:`gestion.Menu`

    ``pay_buttons``
        List of :model:`paymentMethod`

    **Template**

    :template:`gestion/manage.html`
    """
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
    return render(request, "gestion/manage.html", {
        "gestion_form": gestion_form,
        "reload_form": reload_form,
        "refund_form": refund_form,
        "bieresPression": bieresPression,
        "bieresBouteille": bieresBouteille,
        "panini": panini,
        "food": food,
        "soft": soft,
        "menus": menus,
        "pay_buttons": pay_buttons
        })

@csrf_exempt
@active_required
@login_required
@permission_required('gestion.add_consumptionhistory')
def order(request):
    """
    Process the given order. Called by a js/JQuery script.
    """
    if("user" not in request.POST or "paymentMethod" not in request.POST or "amount" not in request.POST or "order" not in request.POST):
        return HttpResponse("Erreur du POST")
    else:
        user = get_object_or_404(User, pk=request.POST['user'])
        paymentMethod = get_object_or_404(PaymentMethod, pk=request.POST['paymentMethod'])
        amount = Decimal(request.POST['amount'])
        order = json.loads(request.POST["order"])
        menus = json.loads(request.POST["menus"])
        listPintes = json.loads(request.POST["listPintes"])
        gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
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
        # Partie un peu complexe : je libère toutes les pintes de la commande, puis je test
        # s'il a trop de pintes non rendues, puis je réalloue les pintes
        for pinte in listPintes:
            allocate(pinte, None)
        if(gp.lost_pintes_allowed and user.profile.nb_pintes >= gp.lost_pintes_allowed):
            return HttpResponse("Impossible de réaliser la commande : l'utilisateur a perdu trop de pintes.")
        for pinte in listPintes:
            allocate(pinte, user)
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
            ch = ConsumptionHistory(customer=user, quantity=quantity, paymentMethod=paymentMethod, product=product, amount=Decimal(quantity*product.amount), coopeman=request.user)
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

@active_required
@login_required
@permission_required('gestion.add_reload')
def reload(request):
    """
    Process a reload request
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
    Cancel a reload
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
    Process a refund request
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
    Cancel a :model:`gestion.ConsumptionHistory`

    ``pk``
        The primary key of the :model:`gestion.ConsumptionHistory` that have to be cancelled
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
    Cancel a :model:`gestion.MenuHistory`

    ``pk``
        The primary key of the :model:`gestion.MenuHistory` that have to be cancelled
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
    Display the products manage static page

    **Template**

    :template:`gestion/products_index.html`
    """
    return render(request, "gestion/products_index.html")

@active_required
@login_required
@permission_required('gestion.add_product')
def addProduct(request):
    """
    Form to add a :model:`gestion.Product`

    **Context**

    ``form``
        The ProductForm instance
    
    ``form_title``
        The title for the form template

    ``form_button``
        The text of the button for the form template

    **Template**

    :template:`form.html`
    """
    form = ProductForm(request.POST or None)
    if(form.is_valid()):
        product = form.save()
        messages.success(request, "Le produit a bien été ajouté")
        return redirect(reverse('gestion:productProfile', kwargs={'pk':product.pk}))
    return render(request, "form.html", {"form": form, "form_title": "Ajout d'un produit", "form_button": "Ajouter"})

@active_required
@login_required
@permission_required('gestion.change_product')
def editProduct(request, pk):
    """
    Form to edit a :model:`gestion.Product`

    ``pk``
        The primary key of the requested :model:`gestion.Product`

    **Context**

    ``form``
        The ProductForm instance
    
    ``form_title``
        The title for the form template

    ``form_button``
        The text of the button for the form template

    **Template**

    :template:`form.html`
    """
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if(form.is_valid()):
        form.save()
        messages.success(request, "Le produit a bien été modifié")
        return redirect(reverse('gestion:productProfile', kwargs={'pk':product.pk}))
    return render(request, "form.html", {"form": form, "form_title": "Modification d'un produit", "form_button": "Modifier"})

@active_required
@login_required
@permission_required('gestion.view_product')
def productsList(request):
    """
    Display the list of :model:`gestion.Product`

    **Context**

    ``products``
        The list of :model:`gestion.Product`

    **Template**

    :template:`gestion/products_list.html`
    """
    products = Product.objects.all()
    return render(request, "gestion/products_list.html", {"products": products})

@active_required
@login_required
@permission_required('gestion.view_product')
def searchProduct(request):
    """
    Form to search a :model:`gestion.Product`

    **Context**

    ``form``
        The SearchProductForm instance
    
    ``form_title``
        The title for the form template

    ``form_button``
        The text of the button for the form template

    **Template**

    :template:`form.html`
    """
    form = SearchProductForm(request.POST or None)
    if(form.is_valid()):
        return redirect(reverse('gestion:productProfile', kwargs={'pk': form.cleaned_data['product'].pk }))
    return render(request, "form.html", {"form": form, "form_title":"Rechercher un produit", "form_button": "Rechercher"})

@active_required
@login_required
@permission_required('gestion.view_product')
def productProfile(request, pk):
    """
    Display the profile of a :model:`gestion.Product`

    ``pk``
        The primary key of the requested :model:`gestion.Product`

    **Context**
    
    ``product``
        The :model:`gestion.Product` instance

    **Template**

    :model:`gestion/product_profile.html`
    """
    product = get_object_or_404(Product, pk=pk)
    return render(request, "gestion/product_profile.html", {"product": product})

@active_required
@login_required
def getProduct(request, pk):
    """
    Get :model:`gestion.Product` by barcode. Called by a js/JQuery script

    ``pk``
        The requested pk
    """
    product = Product.objects.get(pk=pk)
    if product.category == Product.P_PRESSION:
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
    Switch the active status of the requested :model:`gestion.Product`

    ``pk``
        The primary key of the :model:`gestion.Product`
    """
    product = get_object_or_404(Product, pk=pk)
    product.is_active = 1 - product.is_active
    product.save()
    messages.success(request, "La disponibilité du produit a bien été changée")
    return redirect(reverse('gestion:productProfile', kwargs={'pk': product.pk}))

class ProductsAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete view for all :model:`gestion.Product`
    """
    def get_queryset(self):
        qs = Product.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs

class ActiveProductsAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete view for active :model:`gestion.Product`
    """
    def get_queryset(self):
        qs = Product.objects.filter(is_active=True)
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs

########## Kegs ##########

@active_required
@login_required
@permission_required('gestion.add_keg')
def addKeg(request):
    """
    Display a form to add a :model:`gestion.Keg`

    **Context**
    
    ``form``
        The KegForm instance
    
    ``form_title``
        The title for the :template:`form.html` template

    ``form_button``
        The text for the button in :template:`form.html` template

    **Template**

    :template:`form.html`
    """
    form = KegForm(request.POST or None)
    if(form.is_valid()):
        keg = form.save()
        messages.success(request, "Le fût " + keg.name + " a bien été ajouté")
        return redirect(reverse('gestion:kegsList'))
    return render(request, "form.html", {"form":form, "form_title": "Ajout d'un fût", "form_button": "Ajouter"})

@active_required
@login_required
@permission_required('gestion.change_keg')
def editKeg(request, pk):
    """
    Display a form to edit a :model:`gestion.Keg`

    ``pk``
        The primary key of the requested :model:`gestion.Keg`

    **Context**
    
    ``form``
        The KegForm instance
    
    ``form_title``
        The title for the :template:`form.html` template

    ``form_button``
        The text for the button in :template:`form.html` template

    **Template**

    :template:`form.html`
    """
    keg = get_object_or_404(Keg, pk=pk)
    form = KegForm(request.POST or None, instance=keg)
    if(form.is_valid()):
        form.save()
        messages.success(request, "Le fût a bien été modifié")
        return redirect(reverse('gestion:kegsList'))
    return render(request, "form.html", {"form": form, "form_title": "Modification d'un fût", "form_button": "Modifier"})

@active_required
@login_required
@permission_required('gestion.open_keg')
def openKeg(request):
    """
    Display a form to open a :model:`gestion.Keg`

    **Context**
    
    ``form``
        The SelectPositiveKegForm instance
    
    ``form_title``
        The title for the :template:`form.html` template

    ``form_button``
        The text for the button in :template:`form.html` template

    **Template**

    :template:`form.html`
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
    return render(request, "form.html", {"form": form, "form_title":"Percutage d'un fût", "form_button":"Percuter"})

@active_required
@login_required
@permission_required('gestion.open_keg')
def openDirectKeg(request, pk):
    """
    Open the requested :model:`gestion.Keg`

    ``pk``
        The primary key of the :model:`gestion.Keg`
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
    Display a form to close a :model:`gestion.Keg`

    **Context**
    
    ``form``
        The SelectActiveKegForm instance
    
    ``form_title``
        The title for the :template:`form.html` template

    ``form_button``
        The text for the button in :template:`form.html` template

    **Template**

    :template:`form.html`
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
    return render(request, "form.html", {"form": form, "form_title":"Fermeture d'un fût", "form_button":"Fermer le fût"})

@active_required
@login_required
@permission_required('gestion.close_keg')
def closeDirectKeg(request, pk):
    """
    Close the requested :model:`gestion.Keg`

    ``pk``
        The pk of the active :model:`gestion.Keg`
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
    Display the list of :model:`gestion.Keg`

    **Context**

    ``kegs_active``
        List of active :model:`gestion.Keg`

    ``kegs_inactive``
        List of inactive :model:`gestion.Keg`

    **Template**

    :template:`gestion/kegs_list.html`
    """
    kegs_active = KegHistory.objects.filter(isCurrentKegHistory=True)
    ids_actives = kegs_active.values('id')
    kegs_inactive = Keg.objects.exclude(id__in = ids_actives)
    return render(request, "gestion/kegs_list.html", {"kegs_active": kegs_active, "kegs_inactive": kegs_inactive})

@active_required
@login_required
@permission_required('gestion.view_keghistory')
def kegH(request, pk):
    """
    Display the history of requested :model:`gestion.Keg`

    ``pk``
        The primary key of the requested :model:`gestion.Keg`

    **Context**

    ``keg``
        The :model:`gestion.Keg` instance
    
    ``kegHistory``
        List of :model:`gestion.KegHistory` attached to keg

    **Template**

    :template:`gestion/kegh.html`
    """
    keg = get_object_or_404(Keg, pk=pk)
    kegHistory = KegHistory.objects.filter(keg=keg).order_by('-openingDate')
    return render(request, "gestion/kegh.html", {"keg": keg, "kegHistory": kegHistory})

class KegActiveAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete view for active :model:`gestion.Keg`
    """
    def get_queryset(self):
        qs = Keg.objects.filter(is_active = True)
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs

class KegPositiveAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete view for :model:`gestion.Keg` with positive stockHold
    """
    def get_queryset(self):
        qs = Keg.objects.filter(stockHold__gt = 0)
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs

########## Menus ##########

@active_required
@login_required
@permission_required('gestion.add_menu')
def addMenu(request):
    """
    Display a form to add a :model:`gestion.Menu`

    **Context**
    
    ``form``
        The MenuForm instance
    
    ``form_title``
        The title for the :template:`form.html` template

    ``form_button``
        The text for the button in :template:`form.html` template

    **Template**

    :template:`form.html`
    """
    form = MenuForm(request.POST or None)
    extra_css = "#id_articles{height:200px;}"
    if(form.is_valid()):
        menu = form.save()
        messages.success(request, "Le menu " + menu.name + " a bien été ajouté")
        return redirect(reverse('gestion:menusList'))
    return render(request, "form.html", {"form":form, "form_title": "Ajout d'un menu", "form_button": "Ajouter", "extra_css": extra_css})

@active_required
@login_required
@permission_required('gestion.change_menu')
def edit_menu(request, pk):
    """
    Display a form to edit a :model:`gestion.Menu`

    ``pk``
        The primary key of requested :model:`gestion.Menu`

    **Context**
    
    ``form``
        The MenuForm instance
    
    ``form_title``
        The title for the :template:`form.html` template

    ``form_button``
        The text for the button in :template:`form.html` template

    **Template**

    :template:`form.html`
    """
    menu = get_object_or_404(Menu, pk=pk)
    form = MenuForm(request.POST or None, instance=menu)
    extra_css = "#id_articles{height:200px;}"
    if form.is_valid():
        form.save()
        messages.success(request, "Le menu a bien été modifié")
        return redirect(reverse('gestion:menusList'))
    return render(request, "form.html", {"form": form, "form_title": "Modification d'un menu", "form_button": "Modifier", "extra_css": extra_css})

@active_required
@login_required
@permission_required('gestion.view_menu')
def searchMenu(request):
    """
    Search a :model:`gestion.Menu` via SearchMenuForm instance

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

@active_required
@login_required
@permission_required('gestion.view_menu')
def menus_list(request):
    """
    Display the :model:`gestion.Menu` list

    **Context**

    ``menus``
        The list of :model:`gestion.Menu` instances

    **Template**

    :template:`gestion/menus_list.html`
    """
    menus = Menu.objects.all()
    return render(request, "gestion/menus_list.html", {"menus": menus})

@active_required
@login_required
@permission_required('gestion.change_menu')
def switch_activate_menu(request, pk):
    """
    Switch active status of a :model:`gestion.Menu`

    ``pk``
        The pk of the :model:`gestion.Menu`
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
    Search :model:`gestion.Menu` by barcode

    ``pk``
        The requested pk
    """
    menu = get_object_or_404(Menu, pk=pk)
    nb_pintes = 0
    for article in menu.articles:
        if article.category == Product.P_PRESSION:
            nb_pintes +=1
    data = json.dumps({"pk": menu.pk, "barcode" : menu.barcode, "name": menu.name, "amount" : menu.amount, needQuantityButton: False, "nb_pintes": nb_pintes})
    return HttpResponse(data, content_type='application/json')

class MenusAutocomplete(autocomplete.Select2QuerySetView):
    """
    Used as autcomplete for all :model:`gestion.Menu`
    """
    def get_queryset(self):
        qs = Menu.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs

########## Ranking ##########

@active_required
@login_required
def ranking(request):
    """
    Display the ranking page

    **Context**

    ``bestBuyers``
        List of the 25 best buyers

    ``bestDrinkers``
        List of the 25 best drinkers

    **Template**

    :template: `gestion/ranking.html`
    """
    bestBuyers = User.objects.order_by('-profile__debit')[:25]
    customers = User.objects.all()
    list = []
    for customer in customers:
        alcohol = customer.profile.alcohol
        list.append([customer, alcohol])
    bestDrinkers = sorted(list, key=lambda x: x[1], reverse=True)[:25]
    return render(request, "gestion/ranking.html", {"bestBuyers": bestBuyers, "bestDrinkers": bestDrinkers})

########## Pinte monitoring ##########

def allocate(pinte_pk, user):
    """
    Allocate a pinte to a user or release the pinte if user is None
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
    View to release a pinte
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
    return render(request, "form.html", {"form": form, "form_title": "Ajouter des pintes", "form_button": "Ajouter"})

@active_required
@login_required
@permission_required('gestion.change_pinte')
def release_pintes(request):
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
    return render(request, "form.html", {"form": form, "form_title": "Libérer des pintes", "form_button": "Libérer"})

@active_required
@login_required
@permission_required('gestion.view_pinte')
def pintes_list(request):
    free_pintes = Pinte.objects.filter(current_owner=None)
    taken_pintes = Pinte.objects.exclude(current_owner=None)
    return render(request, "gestion/pintes_list.html", {"free_pintes": free_pintes, "taken_pintes": taken_pintes})

@active_required
@login_required
@permission_required('auth.view_user')
def pintes_user_list(request):
    pks = [x.pk for x in User.objects.all() if x.profile.nb_pintes > 0]
    users = User.objects.filter(pk__in=pks)
    return render(request, "gestion/pintes_user_list.html", {"users": users})