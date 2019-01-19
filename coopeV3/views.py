from django.shortcuts import redirect, render
from django.urls import reverse

from preferences.models import GeneralPreferences
from gestion.models import Keg

def home(request):
    if request.user.is_authenticated:
        if(request.user.has_perm('gestion.can_manage')):
            return redirect(reverse('gestion:manage'))
        else:
            return redirect(reverse('homepage'))
    else:
        return redirect(reverse('users:login'))

def homepage(request):
    gp, _ = GeneralPreferences.objects.get_or_create(pk=1)
    kegs = Keg.objects.filter(is_active=True)
    return render(request, "home.html", {"home_text": gp.home_text, "kegs": kegs})
