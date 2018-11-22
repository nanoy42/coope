from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required

from coopeV3.acl import active_required, acl_or

import simplejson as json
from dal import autocomplete
from decimal import *

from .forms import ReloadForm, RefundForm, ProductForm, KegForm, MenuForm, GestionForm, SearchMenuForm, SearchProductForm
from .models import Product, Menu, Keg, ConsumptionHistory
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
    print(request.POST)
    if("user" not in request.POST or "paymentMethod" not in request.POST or "amount" not in request.POST or "order" not in request.POST):
        raise Http404("Erreur du POST")
    else:
        user = get_object_or_404(User, pk=request.POST['user'])
        paymentMethod = get_object_or_404(PaymentMethod, pk=request.POST['paymentMethod'])
        amount = Decimal(request.POST['amount'])
        order = json.loads(request.POST["order"])
        if(len(order) == 0 or amount == 0):
            raise Http404("Pas de commande")
        if(paymentMethod.affect_balance):
            if(user.profile.balance < amount):
                raise Http404("Solde inférieur au prix de la commande")
            else:
                user.profile.debit += amount
                user.save()
        for o in order:
            print(o)
            product = get_object_or_404(Product, pk=o["pk"])
            ch = ConsumptionHistory(customer = user, quantity = int(o["quantity"]), paymentMethod=paymentMethod, product=product, amount=int(o["quantity"])*product.amount, coopeman=request.user)
            ch.save()
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
        return redirect(reverse('gestion:productsIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Ajout d'un produit", "form_button": "Ajouter"})

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
        return redirect(reverse('gestion:productsIndex'))
    return render(request, "form.html", {"form":form, "form_title": "Ajout d'un fût", "form_button": "Ajouter"})


########## Menus ##########

@login_required
@permission_required('gestion.add_menu')
def addMenu(request):
    form = MenuForm(request.POST or None)
    extra_css = "#id_articles{height:200px;}"
    if(form.is_valid()):
        menu = form.save()
        messages.success(request, "Le menu " + menu.name + " a bien été ajouté")
        return redirect(reverse('gestion:productsIndex'))
    return render(request, "form.html", {"form":form, "form_title": "Ajout d'un menu", "form_button": "Ajouter", "extra_css": extra_css})


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
        menu = form.menu
        return redirect(reverse('gestion:changeMenu', kwargs={'pk':menu.pk}))
    return render(request, "form.html", {"form": form, "form_title": "Recherche d'un menu", "form_button": "Modifier"})

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