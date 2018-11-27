from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.decorators import login_required, permission_required

import simplejson as json
from datetime import datetime, timedelta
from dal import autocomplete

from coopeV3.acl import admin_required, superuser_required, self_or_has_perm, active_required
from .models import CotisationHistory, WhiteListHistory, School
from .forms import CreateUserForm, LoginForm, CreateGroupForm, EditGroupForm, SelectUserForm, GroupsEditForm, EditPasswordForm, addCotisationHistoryForm, addCotisationHistoryForm, addWhiteListHistoryForm, SelectNonAdminUserForm, SelectNonSuperUserForm, SchoolForm
from gestion.models import Reload, Consumption, ConsumptionHistory

@active_required
def loginView(request):
    """
    Display the login form for :model:`User`.

    **Context**

    ``form_entete``
        Title of the form.

    ``form``
        The login form.

    ``form_button``
        Content of the form button.

    **Template**

    :template:`form.html`
    """
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

@active_required
@login_required
def logoutView(request):
    """
    Logout the logged user
    """
    logout(request)
    messages.success(request, "Vous êtes à présent déconnecté")
    return redirect(reverse('home'))

@active_required
@login_required
@permission_required('auth.view_user')
def index(request):
    """
    Display the index for user related actions

    **Template**

    :template:`users/index.html`
    """
    return render(request, "users/index.html")

########## users ##########

@active_required
@login_required
@self_or_has_perm('pk', 'auth.view_user')
def profile(request, pk):
    """
    Display the profile for the requested user

    ``pk``
        The primary key for user

    **Context**

    ``user``
        The instance of User
    
    ``self``
        Boolean value wich indicates if the current logged user and the request user are the same

    ``cotisations``
        List of the user's cotisations

    ``whitelists``
        List of the user's whitelists
    
    ``reloads``
        List of the last 5 reloads of the user

    **Template**

    :template:`users/profile.html`
    """
    user = get_object_or_404(User, pk=pk)
    self = request.user == user
    cotisations = CotisationHistory.objects.filter(user=user)
    whitelists = WhiteListHistory.objects.filter(user=user)
    reloads = Reload.objects.filter(customer=user).order_by('-date')
    consumptionsChart = Consumption.objects.filter(customer=user)
    products = []
    quantities = []
    for ch in consumptionsChart:
        if ch.product in products:
            i = products.index(ch.product)
            quantities[i] += ch.quantity
        else:
            products.append(ch.product)
            quantities.append(ch.quantity)
    lastConsumptions = ConsumptionHistory.objects.filter(customer=user).order_by('-date')[:10]
    return render(request, "users/profile.html", 
                {
                    "user":user,
                    "self":self,
                    "cotisations":cotisations,
                    "whitelists": whitelists,
                    "reloads": reloads,
                    "products": products,
                    "quantities": quantities,
                    "lastConsumptions": lastConsumptions
                })

@active_required
@login_required
@permission_required('auth.add_user')
def createUser(request):
    """
    Display a CreateUserForm instance.

    **Context**

    ``form_entete``
        The form title.

    ``form``
        The CreateUserForm instance.

    ``form_button``
        The content of the form button.

    **Template**

    :template:`form.html`
    """
    form = CreateUserForm(request.POST or None)
    if(form.is_valid()):
        user = form.save(commit=False)
        user.set_password(user.username)
        user.save()
        user.profile.school = form.cleaned_data['school']
        user.save()
    return render(request, "form.html", {"form_entete": "Gestion des utilisateurs", "form":form, "form_title":"Création d'un nouvel utilisateur", "form_button":"Créer l'utilisateur"})

@active_required
@login_required
@permission_required('auth.view_user')
def searchUser(request):
    """
    Display a simple searchForm for User.

    **Context**

    ``form_entete``
        The form title.

    ``form``
        The searchForm instance.

    ``form_button``
        The content of the form button.

    **Template**

    :template:`form.html`
    """
    form = SelectUserForm(request.POST or None)
    if(form.is_valid()):
        return redirect(reverse('users:profile', kwargs={"pk":form.cleaned_data['user'].pk}))
    return render(request, "form.html", {"form_entete": "Gestion des utilisateurs", "form": form, "form_title": "Rechercher un utilisateur", "form_button": "Afficher le profil"})

@active_required
@login_required
@permission_required('auth.view_user')
def usersIndex(request):
    """
    Display the list of all users.

    **Context**

    ``users``
        The list of all users
    
    **Template**

    :template:`users/users_index.html`
    """
    users = User.objects.all()
    return render(request, "users/users_index.html", {"users":users})

@active_required
@login_required
@permission_required('auth.change_user')
def editGroups(request, pk):
    """
    Edit the groups of a user.

    ``pk``
        The pk of the user.

    **Context**
    
    ``form_entete``
        The form title.

    ``form``
        The GroupsEditForm instance.

    ``form_button``
        The content of the form button.

    **Template**

    :template:`form.html`
    """
    user = get_object_or_404(User, pk=pk)
    form = GroupsEditForm(request.POST or None, instance=user)
    if(form.is_valid()):
        form.save()
        messages.success(request, "Les groupes de l'utilisateur " + user.username + " ont bien été enregistrés.")
        return redirect(reverse('users:profile', kwargs={'pk':pk}))
    extra_css = "#id_groups{height:200px;}"
    return render(request, "form.html", {"form_entete": "Gestion de l'utilisateur " + user.username, "form": form, "form_title": "Modification des groupes", "form_button": "Enregistrer", "extra_css": extra_css})

@active_required
@login_required
@permission_required('auth.change_user')
def editPassword(request, pk):
    """
    Change the password of a user.

    ``pk``
        The pk of the user.

    **Context**
    ``form_entete``
        The form title.

    ``form``
        The EditPasswordForm instance.

    ``form_button``
        The content of the form button.

    **Template**

    :template:`form.html`
    """
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

@active_required
@login_required
@permission_required('auth.change_user')
def editUser(request, pk):
    """
    Edit a user and user profile

    ``pk``
        The pk of the user.

    **Context**

    ``form_entete``
        The form title.

    ``form``
        The CreateUserForm instance.

    ``form_button``
        The content of the form button.

    **Template**

    :template:`form.html`
    """
    user = get_object_or_404(User, pk=pk)
    form = CreateUserForm(request.POST or None, instance=user, initial = {'school': user.profile.school})
    if(form.is_valid()):
        user.profile.school = form.cleaned_data['school']
        user.save()
        messages.success(request, "Les modifications ont bien été enregistrées")
        return redirect(reverse('users:profile', kwargs={'pk': pk}))
    return render(request, "form.html", {"form_entete":"Modification du compte " + user.username, "form": form, "form_title": "Modification des informations", "form_button": "Modifier"})

@active_required
@login_required
@permission_required('auth.change_user')
def resetPassword(request, pk):
    """
    Reset the password of a user.

    ``pk``
        The pk of the user

    """ 
    user = get_object_or_404(User, pk=pk)
    if user.is_superuser:
        messages.error(request, "Impossible de réinitialiser le mot de passe de " + user.username + " : il est superuser.")
        return redirect(reverse('users:profile', kwargs={'pk': pk}))
    else:
        user.set_password(user.username)
        user.save()
        messages.success(request, "Le mot de passe de " + user.username + " a bien été réinitialisé.")
        return redirect(reverse('users:profile', kwargs={'pk': pk}))

@active_required
@login_required
@permission_required('auth.view_user')
def getUser(request, pk):
    """
    Return username and balance of the requested user (pk)

    ``pk``
        The pk of the user
    """
    user = get_object_or_404(User, pk=pk)
    data = json.dumps({"username": user.username, "balance": user.profile.balance})
    return HttpResponse(data, content_type='application/json')

@active_required
@login_required
@self_or_has_perm('pk', 'auth.view_user')
def allReloads(request, pk, page):
    """
    Display all the reloads of the requested user.

    ``pk``
        The pk of the user.
    ``page``
        The page number.

    **Context**
    
    ``reloads``
        The reloads of the page.
    ``user``
        The requested user

    **Template**

    :template:`users/allReloads.html`
    """
    user = get_object_or_404(User, pk=pk)
    allReloads = Reload.objects.filter(customer=user).order_by('-date')
    paginator = Paginator(allReloads, 2)
    reloads = paginator.get_page(page)
    return render(request, "users/allReloads.html", {"reloads": reloads, "user":user})

########## Groups ##########

@active_required
@login_required
@permission_required('auth.view_group')
def groupsIndex(request):
    """
    Display all the groups.

    **Context**

    ``groups``
        List of all groups.

    **Template**

    :template:`users/groups_index.html`
    """
    groups = Group.objects.all()
    return render(request, "users/groups_index.html", {"groups": groups})

@active_required
@login_required
@permission_required('auth.view_group')
def groupProfile(request, pk):
    """
    Display the profile of a group.

    ``pk``
        The pk of the group.

    **Context**

    ``group``
        The requested group.

    **Template**

    :template:`users/group_profile.html`
    """
    group = get_object_or_404(Group, pk=pk)
    return render(request, "users/group_profile.html", {"group": group})

@active_required
@login_required
@permission_required('auth.add_group')
def createGroup(request):
    """
    Create a group with a CreateGroupForm instance.

    **Context**

    ``form_entete``
        The form title.

    ``form``
        The CreateGroupForm instance.

    ``form_button``
        The content of the form button.

    **Template**

    :template:`form.html`
    """
    form = CreateGroupForm(request.POST or None)
    if(form.is_valid()):
        group = form.save()
        messages.success(request, "Le groupe " + form.cleaned_data['name'] + " a bien été crée.")
        return redirect(reverse('users:groupProfile', kwargs={'pk': group.pk}))
    return render(request, "form.html", {"form_entete": "Gestion des utilisateurs", "form":form, "form_title": "Création d'un groupe de droit", "form_button": "Créer le groupe de droit"})

@active_required
@login_required
@permission_required('auth.change_group')
def editGroup(request, pk):
    """
    Edit a group with a EditGroupForm instance.

    ``pk``
        The pk of the group.

    **Context**

    ``form_entete``
        The form title.

    ``form``
        The EditGroupForm instance.

    ``form_button``
        The content of the form button.

    **Template**

    :template:`form.html`
    """
    group = get_object_or_404(Group, pk=pk)
    form = EditGroupForm(request.POST or None, instance=group)
    extra_css = "#id_permissions{height:200px;}"
    if(form.is_valid()):
        form.save()
        messages.success(request, "Le groupe " + group.name + " a bien été modifié.")
        return redirect(reverse('users:groupProfile', kwargs={'pk': group.pk}))
    return render(request, "form.html", {"form_entete": "Gestion des utilisateurs", "form": form, "form_title": "Modification du groupe de droit " + group.name, "form_button": "Modifier le groupe de droit", "extra_css":extra_css})

@active_required
@login_required
@permission_required('auth.delete_group')
def deleteGroup(request, pk):
    """
    Delete the requested group.

    ``pk``
        The pk of the group
    
    """
    group = get_object_or_404(Group, pk=pk)
    if group.user_set.count() == 0:
        name = group.name
        group.delete()
        messages.success(request, "Le groupe " + name + " a bien été supprimé")
        return redirect(reverse('users:index') + '#second')
    else:
        messages.error(request, "Impossible de supprimer le groupe " + group.name + " : il y a encore des utilisateurs")
        return redirect(reverse('users:groupProfile', kwargs={'pk': group.pk}))

@active_required
@login_required
@permission_required('auth.change_group')
def removeRight(request, groupPk, permissionPk):
    """
    Remove a right from a given group.

    ``groupPk``
        The pk of the group.

    ``permissionPk``
        The pk of the right.

    """
    group = get_object_or_404(Group, pk=groupPk)
    perm = get_object_or_404(Permission, pk=permissionPk)
    if perm in group.permissions.all():
        group.permissions.remove(perm)
        messages.success(request, "La permission " + perm.codename + " a bien été retirée du groupe " + group.name)
    else:
        messages.error(request, "Impossible de retirer la permission " + perm.codename + " du groupe " + group.name)
    return redirect(reverse('users:groupProfile', kwargs={'pk': groupPk}) + "#second")

@active_required
@login_required
@permission_required('auth.change_user')
def removeUser(request, groupPk, userPk):
    """
    Remove a user from a given group.

    ``groupPk``
        The pk of the group.

    ``userPk``
        The pk of the user.

    """
    group = get_object_or_404(Group, pk=groupPk)
    user = get_object_or_404(User, pk=userPk)
    if(group in user.groups.all()):
        user.groups.remove(group)
        messages.success(request, "L'utilisateur " + user.username + " a bien été retiré du groupe " + group.name)
    else:
        messages.error(request, "Impossible de retirer l'utilisateur " + user.username + " du groupe " + group.name)
    return redirect(reverse('users:groupProfile', kwargs={'pk': groupPk}) + "#second")

########## admins ##########

@active_required
@login_required
@admin_required
def adminsIndex(request):
    admins = User.objects.filter(is_staff=True)
    return render(request, "users/admins_index.html", {"admins": admins})

@active_required
@login_required
@admin_required
def addAdmin(request):
    form = SelectNonAdminUserForm(request.POST or None)
    if(form.is_valid()):
        user = form.cleaned_data['user']
        user.is_staff = True
        user.save()
        messages.success(request, "L'utilisateur " + user.username + " a bien été rajouté aux admins")
        return redirect(reverse('users:adminsIndex'))
    return render(request, "form.html", {"form_entete": "Gestion des admins", "form": form, "form_title": "Ajout d'un admin", "form_button":"Ajouter l'utilisateur aux admins"})

@active_required
@login_required
@admin_required
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

@active_required
@login_required
@superuser_required
def superusersIndex(request):
    superusers = User.objects.filter(is_superuser=True)
    return render(request, "users/superusers_index.html", {"superusers": superusers})

@active_required
@login_required
@superuser_required
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

@active_required
@login_required
@superuser_required
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

@active_required
@login_required
@permission_required('users.add_cotisationhistory')
def addCotisationHistory(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = addCotisationHistoryForm(request.POST or None)
    if(form.is_valid()):
        cotisation = form.save(commit=False)
        if(cotisation.paymentMethod.affect_balance):
            if(user.profile.balance >= cotisation.cotisation.amount):
                user.profile.debit += cotisation.cotisation.amount
            else:
                messages.error(request, "Solde insuffisant")
                return redirect(reverse('users:profile',kwargs={'pk':user.pk}))
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

@active_required
@login_required
@permission_required('users.validate_consumptionhistory')
def validateCotisationHistory(request, pk):
    cotisationHistory = get_object_or_404(CotisationHistory, pk=pk)
    cotisationHistory.valid = CotisationHistory.VALID
    cotisationHistory.save()
    messages.success(request, "La cotisation a bien été validée")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))   

@active_required
@login_required
@permission_required('users.validate_consumptionhistory')
def invalidateCotisationHistory(request, pk):
    cotisationHistory = get_object_or_404(CotisationHistory, pk=pk)
    cotisationHistory.valid = CotisationHistory.INVALID
    cotisationHistory.save()
    user = cotisationHistory.user
    user.profile.cotisationEnd = user.profile.cotisationEnd - timedelta(days=cotisationHistory.duration)
    if(cotisationHistory.paymentMethod.affect_balance):
        user.profile.balance += cotisation.amount
    user.save()
    messages.success(request, "La cotisation a bien été invalidée")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

########## Whitelist ##########

@active_required
@login_required
@permission_required('users.add_whitelisthistory')
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
            whiteList.endDate = datetime.now() + timedelta(days=whiteList.duration)
        user.profile.cotisationEnd = whiteList.endDate
        user.save()
        whiteList.save()
        messages.success(request, "L'accès gracieux a bien été ajouté")
        return redirect(reverse('users:profile', kwargs={'pk':user.pk}))
    return render(request, "form.html", {"form": form, "form_title": "Ajout d'un accès gracieux pour " + user.username, "form_button": "Ajouter"})

########## Schools ##########

@active_required
@login_required
@permission_required('users.view_school')
def schoolsIndex(request):
    schools = School.objects.all()
    return render(request, "users/schools_index.html", {"schools": schools})

@active_required
@login_required
@permission_required('users.add_school')
def createSchool(request):
    form = SchoolForm(request.POST or None)
    if(form.is_valid()):
        form.save()
        messages.success(request, "L'école a bien été créée")
        return redirect(reverse('users:schoolsIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Création d'une école", "form_button": "Créer"})

@active_required
@login_required
@permission_required('users.change_school')
def editSchool(request, pk):
    school = get_object_or_404(School, pk=pk)
    form = SchoolForm(request.POST or None, instance=school)
    if(form.is_valid()):
        form.save()
        messages.success(request, "L'école a bien été modifiée")
        return redirect(reverse('users:schoolsIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Modification de l'école " + str(school), "form_button": "Modifier"})

@active_required
@login_required
@permission_required('users.delete_school')
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

class NonAdminUserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = User.objects.filter(is_staff=False)
        if self.q:
            qs = qs.filter(Q(username__istartswith=self.q) | Q(first_name__istartswith=self.q) | Q(last_name__istartswith=self.q))
        return qs