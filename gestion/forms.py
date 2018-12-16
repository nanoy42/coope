from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from dal import autocomplete

from .models import Reload, Refund, Product, Keg, Menu
from preferences.models import PaymentMethod
from coopeV3.widgets import SearchField

class ReloadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ReloadForm, self).__init__(*args, **kwargs)
        self.fields['PaymentMethod'].queryset = PaymentMethod.objects.filter(is_usable_in_reload=True).filter(is_active=True)
        
    class Meta:
        model = Reload
        fields = ("customer", "amount", "PaymentMethod")
        widgets = {'customer': autocomplete.ModelSelect2(url='users:active-users-autocomplete', attrs={'data-minimum-input-length':2})}


class RefundForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = ("customer", "amount")
        widgets = {'customer': autocomplete.ModelSelect2(url='users:active-users-autocomplete', attrs={'data-minimum-input-length':2})}


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

class KegForm(forms.ModelForm):
    class Meta:
        model = Keg
        exclude = ("is_active", )

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = "__all__"

class SearchProductForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), required=True, label="Produit", widget=autocomplete.ModelSelect2(url='gestion:products-autocomplete', attrs={'data-minimum-input-length':2}))

class SearchMenuForm(forms.Form):
    menu = forms.ModelChoiceField(queryset=Menu.objects.all(), required=True, label="Menu", widget=autocomplete.ModelSelect2(url='gestion:menus-autocomplete', attrs={'data-minimum-input-length':2}))

class GestionForm(forms.Form):
    client = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True), required=True, label="Client", widget=autocomplete.ModelSelect2(url='users:active-users-autocomplete', attrs={'data-minimum-input-length':2}))

class SelectPositiveKegForm(forms.Form):
    keg = forms.ModelChoiceField(queryset=Keg.objects.filter(stockHold__gt = 0), required=True, label="Fût", widget=autocomplete.ModelSelect2(url='gestion:kegs-positive-autocomplete'))

class SelectActiveKegForm(forms.Form):
    keg = forms.ModelChoiceField(queryset=Keg.objects.filter(is_active = True), required=True, label="Fût", widget=autocomplete.ModelSelect2(url='gestion:kegs-active-autocomplete'))