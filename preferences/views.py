import simplejson as json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.forms.models import model_to_dict
from django.http import Http404

from coopeV3.acl import active_required

from .models import GeneralPreferences, Cotisation, PaymentMethod, PriceProfile

from .forms import CotisationForm, PaymentMethodForm, GeneralPreferencesForm, PriceProfileForm

@active_required
@login_required
@permission_required('preferences.change_generalpreferences')
def generalPreferences(request):
    """
    View which displays a :class:`~preferences.forms.GeneralPreferencesForm` to edit the :class:`~preferences.models.GeneralPreferences`.
    """
    gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
    form = GeneralPreferencesForm(request.POST or None, request.FILES or None, instance=gp)
    if(form.is_valid()):
        form.save()
        messages.success(request, "Les préférences générales ont bien été mises à jour")
    return render(request, "preferences/general_preferences.html", {"form": form})

########## Cotisations ##########

@active_required
@login_required
@permission_required('preferences.view_cotisation')
def cotisationsIndex(request):
    """
    View which lists all the :class:`~preferences.models.Cotisation`.
    """
    cotisations = Cotisation.objects.all()
    return render(request, "preferences/cotisations_index.html", {"cotisations": cotisations})

@active_required
@login_required
@permission_required('preferences.add_cotisation')
def addCotisation(request):
    """
    View which displays a :class:`~preferences.forms.CotisationForm` to create a :class:`~preferences.models.Cotisation`.
    """
    form = CotisationForm(request.POST or None)
    if(form.is_valid()):
        cotisation = form.save()
        messages.success(request, "La cotisation (" + str(cotisation.duration) + " jours, " + str(cotisation.amount) + "€) a bien été créée")
        return redirect(reverse('preferences:cotisationsIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Création d'une cotisation", "form_button": "Créer", "form_button_icon": "plus-square"})

@active_required
@login_required
@permission_required('preferences.change_cotisation')
def editCotisation(request, pk):
    """
    View which displays a :class:`~preferences.forms.CotisationForm` to edit a :class:`~preferences.models.Cotisation`.

    pk
        The primary key of the :class:`~preferences.models.Cotisation` to edit.
    """
    cotisation = get_object_or_404(Cotisation, pk=pk)
    form = CotisationForm(request.POST or None, instance=cotisation)
    if(form.is_valid()):
        cotisation = form.save()
        messages.success(request, "La cotisation (" + str(cotisation.duration) + " jours, " + str(cotisation.amount) + "€) a bien été modifiée")
        return redirect(reverse('preferences:cotisationsIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Modification d'une cotisation", "form_button": "Modifier", "form_button_icon": "pencil-alt"})

@active_required
@login_required
@permission_required('preferences.delete_cotisation')
def deleteCotisation(request, pk):
    """
    Delete a :class:`~preferences.models.Cotisation`.

    pk
        The primary key of the :class:`~preferences.models.Cotisation` to delete.
    """
    cotisation = get_object_or_404(Cotisation, pk=pk)
    message = "La cotisation (" + str(cotisation.duration) + " jours, " + str(cotisation.amount) + "€) a bien été supprimée"
    cotisation.delete()
    messages.success(request, message)
    return redirect(reverse('preferences:cotisationsIndex'))

@active_required
@login_required
@permission_required('preferences.view_cotisation')
def get_cotisation(request, pk):
    """
    Return the requested :class:`~preferences.models.Cotisation` in json format.

    pk
        The primary key of the requested :class:`~preferences.models.Cotisation`.    
    """
    cotisation = get_object_or_404(Cotisation, pk=pk)
    data = json.dumps({"pk": cotisation.pk, "duration": cotisation.duration, "amount" : cotisation.amount, "needQuantityButton": False})
    return HttpResponse(data, content_type='application/json')

########## Payment Methods ##########

@active_required
@login_required
@permission_required('preferences.view_paymentmethod')
def paymentMethodsIndex(request):
    """
    View which lists all the :class:`~preferences.models.PaymentMethod`.
    """
    paymentMethods =  PaymentMethod.objects.all()
    return render(request, "preferences/payment_methods_index.html", {"paymentMethods": paymentMethods})

@active_required
@login_required
@permission_required('preferences.add_paymentmethod')
def addPaymentMethod(request):
    """
    View which displays a :class:`~preferences.forms.PaymentMethodForm` to create a :class:`~preferences.models.PaymentMethod`.
    """
    form = PaymentMethodForm(request.POST or None)
    if(form.is_valid()):
        paymentMethod = form.save()
        messages.success(request, "Le moyen de paiement " + paymentMethod.name + " a bien été crée")
        return redirect(reverse('preferences:paymentMethodsIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Création d'un moyen de paiement", "form_button": "Créer", "form_button_icon": "plus-square"})

@active_required
@login_required
@permission_required('preferences.change_paymentmethod')
def editPaymentMethod(request, pk):
    """
    View which displays a :class:`~preferences.forms.PaymentMethodForm` to edit a :class:`~preferences.models.PaymentMethod`.

    pk
        The primary key of the :class:`~preferences.models.PaymentMethod` to edit.
    """
    paymentMethod = get_object_or_404(PaymentMethod, pk=pk)
    form = PaymentMethodForm(request.POST or None, instance=paymentMethod)
    if(form.is_valid()):
        paymentMethod = form.save()
        messages.success(request, "Le moyen de paiment " + paymentMethod.name + " a bien été modifié")
        return redirect(reverse('preferences:paymentMethodsIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Modification d'un moyen de paiement", "form_button": "Modifier", "form_button_icon": "pencil-alt"})

@active_required
@login_required
@permission_required('preferences.delete_paymentmethod')
def deletePaymentMethod(request,pk):
    """
    Delete a :class:`~preferences.models.PaymentMethod`.

    pk
        The primary key of the :class:`~preferences.models.PaymentMethod` to delete.
    """
    paymentMethod = get_object_or_404(PaymentMethod, pk=pk)
    message = "Le moyen de paiement " + paymentMethod.name + " a bien été supprimé"
    paymentMethod.delete()
    messages.success(request, message)
    return redirect(reverse('preferences:paymentMethodsIndex'))

########## Active Site ##########

def inactive(request):
    """
    View which displays the inactive message (if the site is inactive).
    """
    gp, _ = GeneralPreferences.objects.get_or_create(pk=1)
    return render(request, 'preferences/inactive.html', {"message": gp.active_message})

########## Config ##########

def get_config(request):
    """
    Load the :class:`~preferences.models.GeneralPreferences` and return it in json format (except for :attr:`~preferences.models.GeneralPreferences.statutes`, :attr:`~preferences.models.GeneralPreferences.rules` and :attr:`~preferences.models.GeneralPreferences.menu`)
    """
    gp, _ = GeneralPreferences.objects.defer("statutes", "rules", "menu").get_or_create(pk=1)
    gp_dict = model_to_dict(gp)
    del gp_dict["statutes"]
    del gp_dict["rules"]
    del gp_dict["menu"]
    del gp_dict["alcohol_charter"]
    data = json.dumps(gp_dict)
    return HttpResponse(data, content_type='application/json')
    
########## Price Profiles ##########

@active_required
@login_required
@permission_required('preferences.view_priceprofile')
def price_profiles_index(request):
    """
    View which lists all the :class:`~preferences.models.PriceProfile`.
    """
    price_profiles = PriceProfile.objects.all()
    return render(request, "preferences/price_profiles_index.html", {"price_profiles": price_profiles})

@active_required
@login_required
@permission_required('preferences.add_priceprofile')
def add_price_profile(request):
    """
    View which displays a :class:`~preferences.forms.PriceProfileForm` to create a :class:`~preferences.models.PriceProfile`.
    """
    form = PriceProfileForm(request.POST or None)
    if form.is_valid():
        price_profile = form.save()
        messages.success(request, "Le profil de prix " + price_profile.name + " a bien été crée")
        return redirect(reverse('preferences:priceProfilesIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Création d'un profil de prix", "form_button": "Créer", "form_button_icon": "plus-square"})

@active_required
@login_required
@permission_required('preferences.change_priceprofile')
def edit_price_profile(request, pk):
    """
    View which displays a :class:`~preferences.forms.PriceProfile` to edit a :class:`~preferences.models.PriceProfile`.

    pk
        The primary key of the :class:`~preferences.models.PriceProfile` to edit.
    """
    price_profile = get_object_or_404(PriceProfile, pk=pk)
    form = PriceProfileForm(request.POST or None, instance=price_profile)
    if form.is_valid():
        price_profile = form.save()
        messages.success(request, "Le profil de prix " + price_profile.name + " a bien été modifié")
        return redirect(reverse('preferences:priceProfilesIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Modification d'un profil de prix", "form_button": "Modifier", "form_button_icon": "pencil-alt"})

@active_required
@login_required
@permission_required('preferences.delete_priceprofile')
def delete_price_profile(request,pk):
    """
    Delete a :class:`~preferences.models.PriceProfile`.

    pk
        The primary key of the :class:`~preferences.models.PriceProfile` to delete.
    """
    price_profile = get_object_or_404(PriceProfile, pk=pk)
    message = "Le profil de prix " + price_profile.name + " a bien été supprimé"
    price_profile.delete()
    messages.success(request, message)
    return redirect(reverse('preferences:priceProfilesIndex'))
