import simplejson as json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.forms.models import model_to_dict

from coopeV3.acl import active_required

from .models import GeneralPreferences, Cotisation, PaymentMethod

from .forms import CotisationForm, PaymentMethodForm, GeneralPreferencesForm

@active_required
@login_required
@permission_required('preferences.change_generalpreferences')
def generalPreferences(request):
    """
    Display form to edit the general preferences

    **Context**

    ``form``
        The GeneralPreferences form instance

    **Template**

    :template:`preferences/general_preferences.html`
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
    Lists the cotisations

    **Context**

    ``cotisations``
        List of cotisations

    **Template**

    :template:`preferences/cotisations_index.html`
    """
    cotisations = Cotisation.objects.all()
    return render(request, "preferences/cotisations_index.html", {"cotisations": cotisations})

@active_required
@login_required
@permission_required('preferences.add_cotisation')
def addCotisation(request):
    """
    Form to add a cotisation

    **Context**

    ``form``
        The CotisationForm form instance

    ``form_title``
        The title of the form

    ``form_button``
        The text of the form button

    **Template**

    :template:`form.html`
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
    Form to edit a cotisation

    ``pk``
        The primary key of the cotisation

    **Context**

    ``form``
        The CotisationForm form instance

    ``form_title``
        The title of the form

    ``form_button``
        The text of the form button

    **Template**

    :template:`form.html`
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
def deleteCotisation(request,pk):
    """
    Delete a cotisation

    ``pk``
        The primary key of the cotisation to delete
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
    Get a cotisation by pk

    ``pk``
        The primary key of the cotisation
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
    Lists the paymentMethods

    **Context**

    ``paymentMethods``
        List of paymentMethods

    **Template**

    :template:`preferences/payment_methods_index.html`
    """
    paymentMethods =  PaymentMethod.objects.all()
    return render(request, "preferences/payment_methods_index.html", {"paymentMethods": paymentMethods})

@active_required
@login_required
@permission_required('preferences.add_paymentmethod')
def addPaymentMethod(request):
    """
    Form to add a paymentMethod

    **Context**

    ``form``
        The CotisationForm form paymentMethod

    ``form_title``
        The title of the form

    ``form_button``
        The text of the form button

    **Template**

    :template:`form.html`
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
    Form to edit a paymentMethod

    ``pk``
        The primary key of the paymentMethod

    **Context**

    ``form``
        The PaymentMethodForm form instance

    ``form_title``
        The title of the form

    ``form_button``
        The text of the form button

    **Template**

    :template:`form.html`
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
    Delete a paymentMethod

    ``pk``
        The primary key of the paymentMethod to delete
    """
    paymentMethod = get_object_or_404(PaymentMethod, pk=pk)
    message = "Le moyen de paiement " + paymentMethod.name + " a bien été supprimé"
    paymentMethod.delete()
    messages.success(request, message)
    return redirect(reverse('preferences:paymentMethodsIndex'))

########## Active Site ##########

def inactive(request):
    """
    Displays inactive view
    """
    gp, _ = GeneralPreferences.objects.get_or_create(pk=1)
    return render(request, 'preferences/inactive.html', {"message": gp.active_message})

########## Config ##########

def get_config(request):
    """
    Load the config and return it in a json format
    """
    gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
    data = json.dumps(model_to_dict(gp))
    return HttpResponse(data, content_type='application/json')
    