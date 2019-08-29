from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


from dal import autocomplete

from .models import Reload, Refund, Product, Keg, Menu, Category
from preferences.models import PaymentMethod, PriceProfile

class ReloadForm(forms.ModelForm):
    """
    A form to create a :class:`~gestion.models.Reload`.
    """
    def __init__(self, *args, **kwargs):
        super(ReloadForm, self).__init__(*args, **kwargs)
        self.fields['PaymentMethod'].queryset = PaymentMethod.objects.filter(is_usable_in_reload=True).filter(is_active=True)
        
    class Meta:
        model = Reload
        fields = ("customer", "amount", "PaymentMethod")
        widgets = {'customer': autocomplete.ModelSelect2(url='users:active-users-autocomplete', attrs={'data-minimum-input-length':2}), 'amount': forms.TextInput}


class RefundForm(forms.ModelForm):
    """
    A form to create a :class:`~gestion.models.Refund`.
    """
    class Meta:
        model = Refund
        fields = ("customer", "amount")
        widgets = {'customer': autocomplete.ModelSelect2(url='users:active-users-autocomplete', attrs={'data-minimum-input-length':2}), 'amount': forms.TextInput}


class ProductForm(forms.ModelForm):
    """
    A form to create and edit a :class:`~gestion.models.Product`.
    """
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {'amount': forms.TextInput}

class CreateKegForm(forms.ModelForm):
    """
    A form to create a :class:`~gestion.models.Keg`.
    """

    class Meta:
        model = Keg
        fields = ["name", "stockHold", "amount", "capacity"]
        widgets = {'amount': forms.TextInput}

    category = forms.ModelChoiceField(queryset=Category.objects.all(), label="Catégorie", help_text="Catégorie dans laquelle placer les produits pinte, demi (et galopin si besoin).")
    deg = forms.DecimalField(max_digits=5, decimal_places=2, label="Degré", validators=[MinValueValidator(0)])
    create_galopin = forms.BooleanField(required=False, label="Créer le produit galopin ?")

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("name")[0:4] != "Fût ":
            raise ValidationError("Le nom du fût doit être sous la forme 'Fût nom de la bière'")

class EditKegForm(forms.ModelForm):
    """
    A form to edit a :class:`~gestion.models.Keg`.
    """

    class Meta:
        model = Keg
        fields = ["name", "stockHold", "amount", "capacity", "pinte", "demi", "galopin"]
        widgets = {'amount': forms.TextInput}

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("name")[0:4] != "Fût ":
            raise ValidationError("Le nom du fût doit être sous la forme 'Fût nom de la bière'")

class MenuForm(forms.ModelForm):
    """
    A form to create and edit a :class:`~gestion.models.Menu`.
    """
    class Meta:
        model = Menu
        fields = "__all__"
        widgets = {'amount': forms.TextInput}

class SearchProductForm(forms.Form):
    """
    A form to search a :class:`~gestion.models.Product`.
    """
    product = forms.ModelChoiceField(queryset=Product.objects.all(), required=True, label="Produit", widget=autocomplete.ModelSelect2(url='gestion:products-autocomplete', attrs={'data-minimum-input-length':2}))

class SearchMenuForm(forms.Form):
    """
    A form to search a :class:`~gestion.models.Menu`.
    """
    menu = forms.ModelChoiceField(queryset=Menu.objects.all(), required=True, label="Menu", widget=autocomplete.ModelSelect2(url='gestion:menus-autocomplete', attrs={'data-minimum-input-length':2}))

class GestionForm(forms.Form):
    """
    A form for the :func:`~gestion.views.manage` view.
    """
    client = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True), required=True, label="Client", widget=autocomplete.ModelSelect2(url='users:active-users-autocomplete', attrs={'data-minimum-input-length':2}))
    product = forms.ModelChoiceField(queryset=Product.objects.filter(is_active=True), required=True, label="Produit", widget=autocomplete.ModelSelect2(url='gestion:active-products-autocomplete', attrs={'data-minimum-input-length':2}))

class SelectPositiveKegForm(forms.Form):
    """
    A form to search a :class:`~gestion.models.Keg` with a positive stockhold.
    """
    keg = forms.ModelChoiceField(queryset=Keg.objects.filter(stockHold__gt = 0), required=True, label="Fût", widget=autocomplete.ModelSelect2(url='gestion:kegs-positive-autocomplete'))

class SelectActiveKegForm(forms.Form):
    """
    A form to search an active :class:`~gestion.models.Keg`.
    """
    keg = forms.ModelChoiceField(queryset=Keg.objects.filter(is_active = True), required=True, label="Fût", widget=autocomplete.ModelSelect2(url='gestion:kegs-active-autocomplete'))

class PinteForm(forms.Form):
    """
    A form to free :class:`Pints <gestion.models.Pinte>`.
    """
    ids = forms.CharField(widget=forms.Textarea, label="Numéros", help_text="Numéros séparés par un espace. Laissez vide pour utiliser le range.", required=False)
    begin = forms.IntegerField(label="Début", help_text="Début du range", required=False)
    end = forms.IntegerField(label="Fin", help_text="Fin du range", required=False)

class GenerateReleveForm(forms.Form):
    """
    A form to generate a releve.
    """
    begin = forms.DateTimeField(label="Date de début")
    end = forms.DateTimeField(label="Date de fin")

class CategoryForm(forms.ModelForm):
    """
    A form to create and edit a :class:`~gestion.models.Category`.
    """
    class Meta:
        model = Category
        fields = "__all__"

class SearchCategoryForm(forms.Form):
    """
    A form to search a :class:`~gestion.models.Category`.
    """
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True, label="Catégorie", widget=autocomplete.ModelSelect2(url='gestion:categories-autocomplete', attrs={'data-minimum-input-length':2}))

class GenerateInvoiceForm(forms.Form):
    """
    A form to generate an invoice
    """
    invoice_date = forms.CharField(label="Date")
    invoice_number = forms.CharField(label="Numéro", help_text="Au format 19018, sans le FE")
    invoice_place = forms.CharField(label="Lieu")
    invoice_object = forms.CharField(label="Objet")
    invoice_description = forms.CharField(label="Description", required=False)
    client_name = forms.CharField(label="Nom du client")
    client_address_fisrt_line = forms.CharField(label="Première ligne d'adresse")
    client_address_second_line = forms.CharField(label="Deuxième ligne d'adresse")
    products = forms.CharField(widget=forms.Textarea, label="Produits", help_text="Au format nom;prix;quantité avec saut de ligne")

class ComputePriceForm(forms.Form):
    """
    A form to compute price
    """
    price_profile = forms.ModelChoiceField(queryset=PriceProfile.objects.all(), label="Profil de prix")
    price = forms.DecimalField(max_digits=10, decimal_places=5, label="Prix")