from django.shortcuts import redirect, render
from django.urls import reverse

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
