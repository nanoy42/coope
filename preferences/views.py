from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required

from coopeV3.acl import active_required

from .models import GeneralPreferences, Cotisation, PaymentMethod

from .forms import CotisationForm, PaymentMethodForm, GeneralPreferencesForm

@active_required
@login_required
@permission_required('preferences.add_generalpreferences')
def generalPreferences(request):
    gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
    form = GeneralPreferencesForm(request.POST or None, instance=gp)
    if(form.is_valid()):
        form.save()
    return render(request, "preferences/general_preferences.html", {"form": form})

########## Cotisations ##########

@active_required
@login_required
@permission_required('preferences.view_cotisation')
def cotisationsIndex(request):
    cotisations = Cotisation.objects.all()
    return render(request, "preferences/cotisations_index.html", {"cotisations": cotisations})

@active_required
@login_required
@permission_required('preferences.add_cotisation')
def addCotisation(request):
    form = CotisationForm(request.POST or None)
    if(form.is_valid()):
        cotisation = form.save()
        messages.success(request, "La cotisation (" + str(cotisation.duration) + " jours, " + str(cotisation.amount) + "€) a bien été créée")
        return redirect(reverse('preferences:cotisationsIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Création d'une cotisation", "form_button": "Créer"})

@active_required
@login_required
@permission_required('preferences.change_cotisation')
def editCotisation(request, pk):
    cotisation = get_object_or_404(Cotisation, pk=pk)
    form = CotisationForm(request.POST or None, instance=cotisation)
    if(form.is_valid()):
        cotisation = form.save()
        messages.success(request, "La cotisation (" + str(cotisation.duration) + " jours, " + str(cotisation.amount) + "€) a bien été modifiée")
        return redirect(reverse('preferences:cotisationsIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Modification d'une cotisation", "form_button": "Modifier"})

@active_required
@login_required
@permission_required('preferences.delete_cotisation')
def deleteCotisation(request,pk):
    cotisation = get_object_or_404(Cotisation, pk=pk)
    message = "La cotisation (" + str(cotisation.duration) + " jours, " + str(cotisation.amount) + "€) a bien été supprimée"
    cotisation.delete()
    messages.success(request, message)
    return redirect(reverse('preferences:cotisationsIndex'))


########## Payment Methods ##########

@active_required
@login_required
@permission_required('preferences.view_paymentmethod')
def paymentMethodsIndex(request):
    paymentMethods =  PaymentMethod.objects.all()
    return render(request, "preferences/payment_methods_index.html", {"paymentMethods": paymentMethods})

@active_required
@login_required
@permission_required('preferences.add_paymentmethod')
def addPaymentMethod(request):
    form = PaymentMethodForm(request.POST or None)
    if(form.is_valid()):
        paymentMethod = form.save()
        messages.success(request, "Le moyen de paiement " + paymentMethod.name + " a bien été crée")
        return redirect(reverse('preferences:paymentMethodsIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Création d'un moyen de paiement", "form_button": "Créer"})

@active_required
@login_required
@permission_required('preferences.change_paymentmethod')
def editPaymentMethod(request, pk):
    paymentMethod = get_object_or_404(PaymentMethod, pk=pk)
    form = PaymentMethodForm(request.POST or None, instance=paymentMethod)
    if(form.is_valid()):
        paymentMethod = form.save()
        messages.success(request, "Le moyen de paiment " + paymentMethod.name + " a bien été modifié")
        return redirect(reverse('preferences:paymentMethodsIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Modification d'un moyen de paiement", "form_button": "Modifier"})

@active_required
@login_required
@permission_required('preferences.delete_paymentmethod')
def deletePaymentMethod(request,pk):
    paymentMethod = get_object_or_404(PaymentMethod, pk=pk)
    message = "Le moyen de paiement " + paymentMethod.name + " a bien été supprimé"
    paymentMethod.delete()
    messages.success(request, message)
    return redirect(reverse('preferences:paymentMethodsIndex'))