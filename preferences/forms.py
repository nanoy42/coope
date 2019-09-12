from django import forms
from django.core.exceptions import ValidationError

from .models import Cotisation, PaymentMethod, GeneralPreferences, PriceProfile, Improvement

class CotisationForm(forms.ModelForm):
    """
    Form to add and edit :class:`~preferences.models.Cotisation`.
    """
    class Meta:
        model = Cotisation
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("amount_ptm") > cleaned_data.get("amount"):
            raise ValidationError("La quantité d'argent donnée au club doit être inférieure à\
                la quantité d'argent totale")

class PaymentMethodForm(forms.ModelForm):
    """
    Form to add and edit :class:`~preferences.models.PaymentMethod`.
    """
    class Meta:
        model = PaymentMethod
        fields = "__all__"

class PriceProfileForm(forms.ModelForm):
    """
    Form to add and edit :class:`~preferences.models.PriceProfile`.
    """
    class Meta:
        model = PriceProfile
        fields = "__all__"

class GeneralPreferencesForm(forms.ModelForm):
    """
    Form to edit the :class:`~preferences.models.GeneralPreferences`.
    """
    class Meta:
        model = GeneralPreferences
        fields = "__all__"
        widgets = {
            'global_message': forms.Textarea(attrs={'placeholder': 'Message global à afficher sur le site'}),
            'active_message': forms.Textarea(attrs={'placeholder': 'Ce message s\'affichera si le site n\'est pas actif'}),
            'president': forms.TextInput(attrs={'placeholder': 'Président'}),
            'secretary': forms.TextInput(attrs={'placeholder': 'Secrétaire'}),
            'treasurer': forms.TextInput(attrs={'placeholder': 'Trésorier'}),
            'phoenixTM_responsible': forms.TextInput(attrs={'placeholder': 'Responsable Phœnix Technopôle Metz'}),
            'home_text': forms.Textarea(attrs={'placeholder': 'Ce message sera affiché sur la page d\'accueil'})
        }


class ImprovementForm(forms.ModelForm):
    """
    Form to create an improvement
    """
    class Meta:
        model = Improvement
        fields = ["title", "mode", "description"]
