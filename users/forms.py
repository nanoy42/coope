from django import forms
from django.contrib.auth.models import User, Group
from dal import autocomplete
from .models import School, CotisationHistory, WhiteListHistory
from preferences.models import PaymentMethod

class LoginForm(forms.Form):
    """
    Form to log in
    """
    username = forms.CharField(max_length=255, label="Nom d'utitisateur")
    password = forms.CharField(max_length=255, widget=forms.PasswordInput, label="Mot de passe")

class CreateUserForm(forms.ModelForm):
    """
    Form to create a new user
    """
    class Meta:
        model = User
        fields = ("username", "last_name", "first_name", "email")

    school = forms.ModelChoiceField(queryset=School.objects.all(), label="École")

class CreateGroupForm(forms.ModelForm):
    """
    Form to create a new group
    """
    class Meta:
        model = Group
        fields = ("name", )

class EditGroupForm(forms.ModelForm):
    """
    Form to edit a group
    """
    class Meta:
        model = Group
        fields = "__all__"

class SelectUserForm(forms.Form):
    """
    Form to select a user from all users
    """
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=True, label="Utilisateur", widget=autocomplete.ModelSelect2(url='users:all-users-autocomplete', attrs={'data-minimum-input-length':2}))

class SelectNonSuperUserForm(forms.Form):
    """
    Form to select a user from all non-superuser users
    """ 
    user = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True), required=True, label="Utilisateur", widget=autocomplete.ModelSelect2(url='users:non-super-users-autocomplete', attrs={'data-minimum-input-length':2}))

class SelectNonAdminUserForm(forms.Form):
    """
    Form to select a user from all non-staff users
    """
    user = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True), required=True, label="Utilisateur", widget=autocomplete.ModelSelect2(url='users:non-admin-users-autocomplete', attrs={'data-minimum-input-length':2}))

class GroupsEditForm(forms.ModelForm):
    """
    Form to edit a user's list of groups
    """
    class Meta:
        model = User
        fields = ("groups", )

class EditPasswordForm(forms.Form):
    """
    Form to change the password of a user
    """
    password = forms.CharField(max_length=255, widget=forms.PasswordInput, label="Mot de passe actuel")
    password1 = forms.CharField(max_length=255, widget=forms.PasswordInput, label="Nouveau mot de passe")
    password2 = forms.CharField(max_length=255, widget=forms.PasswordInput, label="Nouveau mot de passe (répétez)")

    def clean_password2(self):
        """
        Verify if the two new passwords are identical
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne sont pas identiques")
        return password2

class addCotisationHistoryForm(forms.ModelForm):
    """
    Form to add a cotisation to user
    """
    def __init__(self, *args, **kwargs):
        super(addCotisationHistoryForm, self).__init__(*args, **kwargs)
        self.fields['paymentMethod'].queryset = PaymentMethod.objects.filter(is_usable_in_cotisation=True).filter(is_active=True)

    class Meta:
        model = CotisationHistory
        fields = ("cotisation", "paymentMethod")

class addWhiteListHistoryForm(forms.ModelForm):
    """
    Form to add a whitelist to user
    """
    class Meta:
        model = WhiteListHistory
        fields = ("duration", )

class SchoolForm(forms.ModelForm):
    """
    Form to add and edit a school
    """
    class Meta:
        model = School
        fields = "__all__"

class ExportForm(forms.Form):
    QUERY_TYPE_CHOICES = (
        ('all', 'Tous les comptes'),
        ('all_active', 'Tous les comptes actifs'),
        ('adherent', 'Tous les adhérents'),
        ('adherent_active', 'Tous les adhérents actifs')
    )

    FIELDS_CHOICES = (
        ('username', 'Nom d\'utilisateur'),
        ('last_name', 'Nom'),
        ('first_name', 'Prénom'),
        ('email', 'Adresse mail'),
        ('school', 'École'),
        ('balance', 'Solde'),
        ('credit', 'Crédit'),
        ('debit', 'Débit')
    )
    query_type = forms.ChoiceField(choices=QUERY_TYPE_CHOICES, label="Ensemble de la demande")
    fields = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=FIELDS_CHOICES, label="Champs")
    group = forms.ModelChoiceField(queryset=Group.objects.all(), empty_label="Tous les groupes", required=False, label="Groupe")