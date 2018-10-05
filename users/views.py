from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect

import json
from datetime import datetime, timedelta

from dal import autocomplete

from .models import CotisationHistory, WhiteListHistory, School
from .forms import CreateUserForm, LoginForm, CreateGroupForm, EditGroupForm, SelectUserForm, GroupsEditForm, EditPasswordForm, addCotisationHistoryForm, addCotisationHistoryForm, addWhiteListHistoryForm, SelectNonAdminUserForm, SelectNonSuperUserForm, SchoolForm

def loginView(request):
    form = LoginForm(request.POST or None)
    if(form.is_valid()):
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user is not None:
            login(request, user)
            messages.success(request, "Vous êtes à présent connecté sous le compte " + str(user))
            if(request.user.has_perm('gestion.can_manage')):
               return redirect(reverse('gestion:manage'))
            else:
               return redirect(reverse('users:profile', kwargs={'pk':request.user.pk}))
        else:
            messages.error(request, "Nom d'utilisateur et/ou mot de passe invalide")
    return render(request, "form.html", {"form_entete": "Connexion", "form": form, "form_title": "Connexion", "form_button": "Se connecter"})

def logoutView(request):
    logout(request)
    messages.success(request, "Vous êtes à présent déconnecté")
    return redirect(reverse('home'))

def index(request):
    return render(request, "users/index.html")

########## schools ##########

########## users ##########

def profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    self = request.user == user
    cotisations = CotisationHistory.objects.filter(user=user)
    whitelists = WhiteListHistory.objects.filter(user=user)
    return render(request, "users/profile.html", {"user":user, "self":self, "cotisations":cotisations, "whitelists": whitelists})

def createUser(request):
    form = CreateUserForm(request.POST or None)
    if(form.is_valid()):
        user = form.save(commit=False)
        user.set_password(user.username)
        user.save()
        user.profile.school = form.cleaned_data['school']
        user.save()
    return render(request, "form.html", {"form_entete": "Gestion des utilisateurs", "form":form, "form_title":"Création d'un nouvel utilisateur", "form_button":"Créer l'utilisateur"})

def searchUser(request):
    form = SelectUserForm(request.POST or None)
    if(form.is_valid()):
        return redirect(reverse('users:profile', kwargs={"pk":form.cleaned_data['user'].pk}))
    return render(request, "form.html", {"form_entete": "Gestion des utilisateurs", "form": form, "form_title": "Rechercher un utilisateur", "form_button": "Afficher le profil"})

def usersIndex(request):
    users = User.objects.all()
    return render(request, "users/users_index.html", {"users":users})

def editGroups(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = GroupsEditForm(request.POST or None, instance=user)
    if(form.is_valid()):
        form.save()
        messages.success(request, "Les groupes de l'utilisateur " + user.username + " ont bien été enregistrés.")
        return redirect(reverse('users:profile', kwargs={'pk':pk}))
    extra_css = "#id_groups{height:200px;}"
    return render(request, "form.html", {"form_entete": "Gestion de l'utilisateur " + user.username, "form": form, "form_title": "Modification des groupes", "form_button": "Enregistrer", "extra_css": extra_css})

def editPassword(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user != request.user:
        messages.error(request, "Vous ne pouvez modifier le mot de passe d'un autre utilisateur")
        return redirect(reverse('home'))
    else:
        form = EditPasswordForm(request.POST or None)
        if(form.is_valid()):
            if authenticate(username=user.username, password = form.cleaned_data['password']) is not None:
                user.set_password(form.cleaned_data['password2'])
                user.save()
                messages.success(request, "Votre mot de passe a bien été mis à jour")
                return redirect(reverse('users:profile', kwargs={'pk':pk}))
            else:
                messages.error(request, "Le mot de passe actuel est incorrect")
        return render(request, "form.html", {"form_entete": "Modification de mon compte", "form": form, "form_title": "Modification de mon mot de passe", "form_button": "Modifier mon mot de passe"})

def editUser(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = CreateUserForm(request.POST or None, instance=user, initial = {'school': user.profile.school})
    if(form.is_valid()):
        user.profile.school = form.cleaned_data['school']
        user.save()
        messages.success(request, "Les modifications ont bien été enregistrées")
        return redirect(reverse('users:profile', kwargs={'pk': pk}))
    return render(request, "form.html", {"form_entete":"Modification du compte " + user.username, "form": form, "form_title": "Modification des informations", "form_button": "Modifier"})

def resetPassword(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.is_superuser:
        messages.error(request, "Impossible de réinitialiser le mot de passe de " + user.username + " : il est superuser.")
        return redirect(reverse('users:profile', kwargs={'pk': pk}))
    else:
        user.set_password(user.username)
        user.save()
        messages.success(request, "Le mot de passe de " + user.username + " a bien été réinitialisé.")
        return redirect(reverse('users:profile', kwargs={'pk': pk}))

def getUser(request, pk):
    user = get_object_or_404(User, pk=pk)
    data = json.dumps({"username": user.username, "balance": float(user.profile.balance)})
    return HttpResponse(data, content_type='application/json')

########## Groups ##########

def groupsIndex(request):
    groups = Group.objects.all()
    return render(request, "users/groups_index.html", {"groups": groups})

def groupProfile(request, pk):
    group = get_object_or_404(Group, pk=pk)
    return render(request, "users/group_profile.html", {"group": group})

def createGroup(request):
    form = CreateGroupForm(request.POST or None)
    if(form.is_valid()):
        group = form.save()
        messages.success(request, "Le groupe " + form.cleaned_data['name'] + " a bien été crée.")
        return redirect(reverse('users:groupProfile', kwargs={'pk': group.pk}))
    return render(request, "form.html", {"form_entete": "Gestion des utilisateurs", "form":form, "form_title": "Création d'un groupe de droit", "form_button": "Créer le groupe de droit"})

def editGroup(request, pk):
    group = get_object_or_404(Group, pk=pk)
    form = EditGroupForm(request.POST or None, instance=group)
    extra_css = "#id_permissions{height:200px;}"
    if(form.is_valid()):
        form.save()
        messages.success(request, "Le groupe " + group.name + " a bien été modifié.")
        return redirect(reverse('users:groupProfile', kwargs={'pk': group.pk}))
    return render(request, "form.html", {"form_entete": "Gestion des utilisateurs", "form": form, "form_title": "Modification du groupe de droit " + group.name, "form_button": "Modifier le groupe de droit", "extra_css":extra_css})

def deleteGroup(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if group.user_set.count() == 0:
        name = group.name
        group.delete()
        messages.success(request, "Le groupe " + name + " a bien été supprimé")
        return redirect(reverse('users:index') + '#second')
    else:
        messages.error(request, "Impossible de supprimer le groupe " + group.name + " : il y a encore des utilisateurs")
        return redirect(reverse('users:groupProfile', kwargs={'pk': group.pk}))

def removeRight(request, groupPk, permissionPk):
    group = get_object_or_404(Group, pk=groupPk)
    perm = get_object_or_404(Permission, pk=permissionPk)
    if perm in group.permissions.all():
        group.permissions.remove(perm)
        messages.success(request, "La permission " + perm.codename + " a bien été retirée du groupe " + group.name)
    else:
        messages.error(request, "Impossible de retirer la permission " + perm.codename + " du groupe " + group.name)
    return redirect(reverse('users:groupProfile', kwargs={'pk': groupPk}) + "#second")

def removeUser(request, groupPk, userPk):
    group = get_object_or_404(Group, pk=groupPk)
    user = get_object_or_404(User, pk=userPk)
    if(group in user.groups.all()):
        user.groups.remove(group)
        messages.success(request, "L'utilisateur " + user.username + " a bien été retiré du groupe " + group.name)
    else:
        messages.error(request, "Impossible de retirer l'utilisateur " + user.username + " du groupe " + group.name)
    return redirect(reverse('users:groupProfile', kwargs={'pk': groupPk}) + "#second")

########## admins ##########

def adminsIndex(request):
    admins = User.objects.filter(is_staff=True)
    return render(request, "users/admins_index.html", {"admins": admins})

def addAdmin(request):
    form = SelectNonAdminUserForm(request.POST or None)
    if(form.is_valid()):
        user = form.cleaned_data['user']
        user.is_staff = True
        user.save()
        messages.success(request, "L'utilisateur " + user.username + " a bien été rajouté aux admins")
        return redirect(reverse('users:adminsIndex'))
    return render(request, "form.html", {"form_entete": "Gestion des admins", "form": form, "form_title": "Ajout d'un admin", "form_button":"Ajouter l'utilisateur aux admins"})

def removeAdmin(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.is_staff:
        if user.is_superuser:
           messages.error(request, "Impossible de retirer l'utilisateur " + user.username + " des admins : il est superuser")
        else:
            if User.objects.filter(is_staff=True).count() > 1:
                user.is_staff = False
                user.save()
                messages.success(request, "L'utilisateur " + user.username + " a bien été retiré des admins.")
            else:
                messages.error(request, "Impossible de retirer l'utilisateur " + user.username + " des admins : il doit en rester au moins un.")
    else:
        messages.error(request, "Impossible de retirer l'utilisateur " + user.username + " des admins : il n'en fait pas partie.")
    return redirect(reverse('users:adminsIndex'))

########## superusers ##########

def superusersIndex(request):
    superusers = User.objects.filter(is_superuser=True)
    return render(request, "users/superusers_index.html", {"superusers": superusers})

def addSuperuser(request):
    form = SelectNonSuperUserForm(request.POST or None)
    if(form.is_valid()):
        user = form.cleaned_data['user']
        user.is_admin = True
        user.is_superuser = True
        user.save()
        messages.success(request, "L'utilisateur " + user.username + " a bien été rajouté aux superusers")
        return redirect(reverse('users:superusersIndex'))
    return render(request, "form.html", {"form_entete": "Gestion des superusers", "form": form, "form_title": "Ajout d'un superuser", "form_button":"Ajouter l'utilisateur aux superusers"})

def removeSuperuser(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.is_superuser:
        if User.objects.filter(is_superuser=True).count() > 1:
            user.is_superuser = False
            user.save()
            messages.success(request, "L'utilisateur " + user.username + " a bien été retiré des superusers.")
        else:
            messages.error(request, "Impossible de retirer l'utilisateur " + user.username + " des superusers : il doit en rester au moins un.")
    else:
        messages.error(request, "Impossible de retirer l'utilisateur " + user.username + " des superusers : il n'en fait pas partie.")
    return redirect(reverse('users:superusersIndex'))

########## Cotisations ##########

def addCotisationHistory(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = addCotisationHistoryForm(request.POST or None)
    if(form.is_valid()):
        cotisation = form.save(commit=False)
        cotisation.user = user
        cotisation.coopeman = request.user
        cotisation.amount = cotisation.cotisation.amount
        cotisation.duration = cotisation.cotisation.duration
        if(user.profile.cotisationEnd):
            cotisation.endDate = user.profile.cotisationEnd + timedelta(days=cotisation.cotisation.duration)
        else:
            cotisation.endDate = datetime.now() + timedelta(days=cotisation.cotisation.duration)
        user.profile.cotisationEnd = cotisation.endDate
        user.save()
        cotisation.save()
        messages.success(request, "La cotisation a bien été ajoutée")
        return redirect(reverse('users:profile',kwargs={'pk':user.pk}))
    return render(request, "form.html",{"form": form, "form_title": "Ajout d'une cotisation pour l'utilisateur " + str(user), "form_button": "Ajouter"})

def validateCotisationHistory(request, pk):
    cotisationHistory = get_object_or_404(CotisationHistory, pk=pk)
    cotisationHistory.valid = CotisationHistory.VALID
    cotisationHistory.save()
    messages.success(request, "La cotisation a bien été validée")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))   

def invalidateCotisationHistory(request, pk):
    cotisationHistory = get_object_or_404(CotisationHistory, pk=pk)
    cotisationHistory.valid = CotisationHistory.INVALID
    cotisationHistory.save()
    user = cotisationHistory.user
    user.profile.cotisationEnd = user.profile.cotisationEnd - timedelta(days=cotisationHistory.duration)
    user.save()
    messages.success(request, "La cotisation a bien été invalidée")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

########## Whitelist ##########

def addWhiteListHistory(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = addWhiteListHistoryForm(request.POST or None)
    if(form.is_valid()):
        whiteList = form.save(commit=False)
        whiteList.user = user
        whiteList.coopeman = request.user
        if(user.profile.cotisationEnd):
            whiteList.endDate = user.profile.cotisationEnd + timedelta(days=whiteList.duration)
        else:
            whiteList = datetime.now() + timedelta(days=whiteList.duration)
        user.profile.cotisationEnd = whiteList.endDate
        user.save()
        whiteList.save()
        messages.success(request, "L'accès gracieux a bien été ajouté")
        return redirect(reverse('users:profile', kwargs={'pk':user.pk}))
    return render(request, "form.html", {"form": form, "form_title": "Ajout d'un accès gracieux pour " + user.username, "form_button": "Ajouter"})

########## Schools ##########

def schoolsIndex(request):
    schools = School.objects.all()
    return render(request, "users/schools_index.html", {"schools": schools})

def createSchool(request):
    form = SchoolForm(request.POST or None)
    if(form.is_valid()):
        form.save()
        messages.success(request, "L'école a bien été créée")
        return redirect(reverse('users:schoolsIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Création d'une école", "form_button": "Créer"})

def editSchool(request, pk):
    school = get_object_or_404(School, pk=pk)
    form = SchoolForm(request.POST or None, instance=school)
    if(form.is_valid()):
        form.save()
        messages.success(request, "L'école a bien été modifiée")
        return redirect(reverse('users:schoolsIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Modification de l'école " + str(school), "form_button": "Modifier"})

def deleteSchool(request, pk):
    school = get_object_or_404(School, pk=pk)
    message = "L'école " + str(school) + " a bien été supprimée"
    school.delete()
    messages.success(request, message)
    return redirect(reverse('users:schoolsIndex'))

########## Autocomplete searchs ##########

class AllUsersAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = User.objects.all()
        if self.q:
            qs = qs.filter(Q(username__istartswith=self.q) | Q(first_name__istartswith=self.q) | Q(last_name__istartswith=self.q))
        return qs

class ActiveUsersAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = User.objects.filter(is_active=True)
        if self.q:
            qs = qs.filter(Q(username__istartswith=self.q) | Q(first_name__istartswith=self.q) | Q(last_name__istartswith=self.q))
        return qs

class AdherentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = User.objects.all()
        return qs

class NonSuperUserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = User.objects.filter(is_superuser=False)
        if self.q:
            qs = qs.filter(Q(username__istartswith=self.q) | Q(first_name__istartswith=self.q) | Q(last_name__istartswith=self.q))
        return qs