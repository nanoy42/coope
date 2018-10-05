from django import forms
from django.contrib.auth.models import User

from dal import autocomplete

from .models import Reload, Refund, Product, Keg, Menu
from preferences.models import PaymentMethod
from coopeV3.widgets import SearchField

class ReloadForm(forms.ModelForm):
    class Meta:
        model = Reload
        fields = ("customer", "amount", "PaymentMethod")

class RefundForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = ("customer", "amount")

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

class KegForm(forms.ModelForm):
    class Meta:
        model = Keg
        fields = "__all__"

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = "__all__"

class GestionForm(forms.Form):
    client = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True), required=True, label="Client", widget=autocomplete.ModelSelect2(url='users:active-users-autocomplete', attrs={'data-minimum-input-length':2}))
    paymentMethod = forms.ModelChoiceField(queryset=PaymentMethod.objects.all(), required=True, label="Moyen de paiement")
