import os

from django.shortcuts import redirect, render
from django.urls import reverse
from django.conf import settings

from preferences.models import GeneralPreferences
from gestion.models import Keg

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