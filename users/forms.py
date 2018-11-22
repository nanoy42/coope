from django import forms
from django.contrib.auth.models import User, Group
from dal import autocomplete
from .models import School, CotisationHistory, WhiteListHistory

class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, label="Nom d'utitisateur")
    password = forms.CharField(max_length=255, widget=forms.PasswordInput, label="Mot de passe")

class CreateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "last_name", "first_name", "email")

    school = forms.ModelChoiceField(queryset=School.objects.all(), label="École")

class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ("name", )

class EditGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = "__all__"

class SelectUserForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=True, label="Utilisateur", widget=autocomplete.ModelSelect2(url='users:all-users-autocomplete', attrs={'data-minimum-input-length':2}))

class SelectNonSuperUserForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True), required=True, label="Utilisateur", widget=autocomplete.ModelSelect2(url='users:non-super-users-autocomplete', attrs={'data-minimum-input-length':2}))

class SelectNonAdminUserForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.filter(is_active=True), required=True, label="Utilisateur", widget=autocomplete.ModelSelect2(url='users:non-admin-users-autocomplete', attrs={'data-minimum-input-length':2}))

class GroupsEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("groups", )

class EditPasswordForm(forms.Form):
    password = forms.CharField(max_length=255, widget=forms.PasswordInput, label="Mot de passe actuel")
    password1 = forms.CharField(max_length=255, widget=forms.PasswordInput, label="Nouveau mot de passe")
    password2 = forms.CharField(max_length=255, widget=forms.PasswordInput, label="Nouveau mot de passe (répétez)")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne sont pas identiques")
        return password2

class addCotisationHistoryForm(forms.ModelForm):
    class Meta:
        model = CotisationHistory
        fields = ("cotisation", "paymentMethod")

class addWhiteListHistoryForm(forms.ModelForm):
    class Meta:
        model = WhiteListHistory
        fields = ("duration", )

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = "__all__"