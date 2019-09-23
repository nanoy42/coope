from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required

from coopeV3.acl import active_required
from gestion.models import Product, Menu, Keg

@active_required
@login_required
def search(request):
    q = request.GET.get("q")
    if q:
        users = User.objects.filter(Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q))
        products = Product.objects.filter(name__icontains=q)
        kegs = Keg.objects.filter(name__icontains=q)
        menus = Menu.objects.filter(name__icontains=q)
        groups = Group.objects.filter(name__icontains=q)
    else:
        users = User.objects.none()
        products = Product.objects.none()
        kegs = Keg.objects.none()
        menus = Menu.objects.none()
        groups = Group.objects.none()
    return render(request, "search/search.html", {"q": q, "users": users, "products": products, "kegs": kegs, "menus": menus, "groups": groups})