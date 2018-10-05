from django import forms

from .models import Cotisation, PaymentMethod, GeneralPreferences

class CotisationForm(forms.ModelForm):
    class Meta:
        model = Cotisation
        fields = "__all__"

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = "__all__"


class GeneralPreferencesForm(forms.ModelForm):
    class Meta:
        model = GeneralPreferences
        fields = "__all__"
        widgets = {
            'global_message': forms.Textarea(attrs={'placeholder': 'Message global à afficher sur le site'}),
            'active_message': forms.Textarea(attrs={'placeholder': 'Ce message s\'affichera si le site n\'est pas actif'}),
            'president': forms.TextInput(attrs={'placeholder': 'Président'}),
            'vice_president': forms.TextInput(attrs={'placeholder': 'Vice-président'}),
            'secretary': forms.TextInput(attrs={'placeholder': 'Secrétaire'}),
            'treasurer': forms.TextInput(attrs={'placeholder': 'Trésorier'}),
            'brewer': forms.TextInput(attrs={'placeholder': 'Maître brasseur'}),
            'grocer': forms.TextInput(attrs={'placeholder': 'Epic épicier'}),
        }

