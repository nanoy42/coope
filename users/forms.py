from django import forms
from django.contrib.auth.models import User, Group

from .models import School
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
    def __init__(self, *args, **kwargs):
        restrictTo = kwargs.pop("restrictTo") or None
        if(restrictTo == "non-superusers"):
            self.queryset = User.objects.filter(is_superuser=False)
        elif(restrictTo == "non-admins"):
            self.queryset = User.objects.filter(is_staff=False)
        else:
            self.queryset = User.objects.all()
        super(SelectUserForm, self).__init__(*args, **kwargs)
        self.fields['user'].queryset = self.queryset
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Utilisateur")
