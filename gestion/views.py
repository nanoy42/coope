from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.models import User

import json
from dal import autocomplete

from .forms import ReloadForm, RefundForm, ProductForm, KegForm, MenuForm, GestionForm
from .models import Product, Menu, Keg

def manage(request):
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
    return render(request, "gestion/manage.html", {"gestion_form": gestion_form, "reload_form": reload_form, "refund_form": refund_form, "bieresPression": bieresPression, "bieresBouteille": bieresBouteille, "panini": panini, "food": food, "soft": soft, "menus": menus})

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

def productsIndex(request):
    return render(request, "gestion/products_index.html")

def addProduct(request):
    form = ProductForm(request.POST or None)
    if(form.is_valid()):
        form.save()
        messages.success(request, "Le produit a bien été ajouté")
        return redirect(reverse('gestion:productsIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Ajout d'un produit", "form_button": "Ajouter"})

def productsList(request):
    products = Product.objects.all()
    return render(request, "gestion/products_list.html", {"products": products})

def getProduct(request, barcode):
    product = Product.objects.get(barcode=barcode)
    data = json.dumps({"pk": product.pk, "barcode" : product.barcode, "name": product.name, "amount" : float(product.amount)})
    return HttpResponse(data, content_type='application/json')


########## Kegs ##########

def addKeg(request):
    form = KegForm(request.POST or None)
    if(form.is_valid()):
        keg = form.save()
        messages.success(request, "Le fût " + keg.name + " a bien été ajouté")
        return redirect(reverse('gestion:productsIndex'))
    return render(request, "form.html", {"form":form, "form_title": "Ajout d'un fût", "form_button": "Ajouter"})


########## Menus ##########

def addMenu(request):
    form = MenuForm(request.POST or None)
    extra_css = "#id_articles{height:200px;}"
    if(form.is_valid()):
        menu = form.save()
        messages.success(request, "Le menu " + menu.name + " a bien été ajouté")
        return redirect(reverse('gestion:productsIndex'))
    return render(request, "form.html", {"form":form, "form_title": "Ajout d'un menu", "form_button": "Ajouter", "extra_css": extra_css})

