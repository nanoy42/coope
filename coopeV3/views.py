import os

from django.shortcuts import redirect, render
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group

from preferences.models import GeneralPreferences, PaymentMethod, Cotisation
from gestion.models import Keg, ConsumptionHistory, Category, Product, Menu
from users.models import School


from .acl import active_required, admin_required

def home(request):
    """
    Redirect the user either to :func:`~gestion.views.manage` view (if connected and staff) or :func:`~coopeV3.views.homepage` view (if connected and not staff) or :func:`~users.views.loginView` view (if not connected).
    """
    if request.user.is_authenticated:
        if(request.user.has_perm('gestion.can_manage')):
            return redirect(reverse('gestion:manage'))
        else:
            return redirect(reverse('homepage'))
    else:
        return redirect(reverse('users:login'))

def homepage(request):
    """
    View which displays the :attr:`~preferences.models.GeneralPreferences.home_text` and active :class:`Kegs <gestion.models.Keg>`.
    """
    gp, _ = GeneralPreferences.objects.get_or_create(pk=1)
    kegs = Keg.objects.filter(is_active=True)
    return render(request, "home.html", {"home_text": gp.home_text, "kegs": kegs})

def coope_runner(request):
    """
    Just an easter egg
    """
    return render(request, "coope-runner.html")


def about(request):
    """
    A page about the project
    """
    os.system("git -C " + settings.BASE_DIR + " shortlog -n $@ | grep \"):\" | sed 's|:||' >> " + settings.BASE_DIR + "/contributors.txt")
    contributors = []
    with open(settings.BASE_DIR + "/contributors.txt", "r") as f:
        for line in f:
            print(line)
            print(line.split(" ")[0])
            contributors.append((line.split(" ")[0], int(line.split(" ")[1].replace("(", "").replace(")", "").replace("\n", ""))))
    os.system("rm " + settings.BASE_DIR + "/contributors.txt")
    license = []
    with open(settings.BASE_DIR + "/LICENSE", "r") as f:
        for line in f:
            license.append(line)
    return render(request, "about.html", {"contributors": contributors, "license": license})

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
    gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
    nb_quotes = len(gp.global_message.split("\n"))
    return render(request, "stats.html", {
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
        "nb_quotes": nb_quotes,
    })