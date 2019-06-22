from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.decorators import login_required, permission_required
from django.forms.models import model_to_dict
from django.utils import timezone
from django.conf import settings

import simplejson as json
from datetime import datetime, timedelta
from dal import autocomplete
import csv
import os


from django_tex.views import render_to_pdf
from coopeV3.acl import admin_required, superuser_required, self_or_has_perm, active_required
from .models import CotisationHistory, WhiteListHistory, School
from .forms import CreateUserForm, LoginForm, CreateGroupForm, EditGroupForm, SelectUserForm, GroupsEditForm, EditPasswordForm, addCotisationHistoryForm, addCotisationHistoryForm, addWhiteListHistoryForm, SelectNonAdminUserForm, SelectNonSuperUserForm, SchoolForm, ExportForm
from gestion.models import Reload, Consumption, ConsumptionHistory, MenuHistory

@active_required
def loginView(request):
    """
    Displays the :class:`users.forms.LoginForm`.
    """
    form = LoginForm(request.POST or None)
    if(form.is_valid()):
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user is not None:
            login(request, user)
            messages.success(request, "Vous êtes à présent connecté sous le compte " + str(user))
            return redirect(reverse('home'))
        else:
            messages.error(request, "Nom d'utilisateur et/ou mot de passe invalide")
    return render(request, "form.html", {"form_entete": "Connexion", "form": form, "form_title": "Connexion", "form_button": "Se connecter", "form_button_icon": "sign-in-alt"})

@active_required
@login_required
def logoutView(request):
    """
    Logout the logged user (:class:`django.contrib.auth.models.User`).
    """
    logout(request)
    messages.success(request, "Vous êtes à présent déconnecté")
    return redirect(reverse('home'))

@active_required
@login_required
@permission_required('auth.view_user')
def index(request):
    """
    Display the index for user related actions.
    """
    export_form = ExportForm(request.POST or None)
    return render(request, "users/index.html", {"export_form": export_form})

def export_csv(request):
    """
    Displays a :class:`users.forms.ExportForm` to export csv files of users.
    """
    export_form = ExportForm(request.POST or None)
    if export_form.is_valid():
        users = User.objects
        qt = export_form.cleaned_data['query_type']
        if qt == 'all':
            filename = "Utilisateurs-coope"
            if not export_form.cleaned_data['group']:
                users = users.all()
        elif qt == 'all_active':
            users = users.filter(is_active=True)
            filename = "Utilisateurs-actifs-coope"
        elif qt == 'adherent':
            pks = [x.pk for x in User.objects.all() if x.profile.is_adherent]
            users = users.filter(pk__in=pks)
            filename = "Adherents-coope"
        elif qt == 'adherent_active':
            pks = [x.pk for x in User.objects.filter(is_active=True) if x.profile.is_adherent]
            users = users.filter(pk__in=pks)
            filename = "Adherents-actifs-coope"
        if export_form.cleaned_data['group']:
            group = export_form.cleaned_data['group']
            users = users.filter(groups=group)
            filename += "(" + group.name + ")"
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="'+ filename + '.csv"'
        writer = csv.writer(response)
        fields = export_form.cleaned_data['fields']
        top = ["#"]
        for field in fields:
            top.append(dict(ExportForm.FIELDS_CHOICES)[field])
        writer.writerow(top)
        for user in users:
            row = [user.pk]
            for field in fields:
                r = getattr(user.profile, field, None)
                if r is not None:
                    row.append(str(r))
            writer.writerow(row)
        return response
    else:
        return redirect(reverse('users:index'))

########## users ##########

@active_required
@login_required
@self_or_has_perm('pk', 'auth.view_user')
def profile(request, pk):
    """
    Displays the profile for the requested user (:class:`django.contrib.auth.models.User`).

    pk
        The primary key of the user (:class:`django.contrib.auth.models.User`) to display profile
    """
    user = get_object_or_404(User, pk=pk)
    self = request.user == user
    cotisations = CotisationHistory.objects.filter(user=user).order_by('-paymentDate')
    whitelists = WhiteListHistory.objects.filter(user=user)
    reloads = Reload.objects.filter(customer=user).order_by('-date')[:5]
    consumptionsChart = Consumption.objects.filter(customer=user)
    products_pre = []
    quantities_pre = []
    for ch in consumptionsChart:
        if ch.product in products_pre:
            i = products_pre.index(ch.product)
            quantities_pre[i] += int(ch.quantity/ch.product.showingMultiplier)
        else:
            products_pre.append(ch.product)
            quantities_pre.append(int(ch.quantity/ch.product.showingMultiplier))
    tot = len(products_pre)
    totQ = sum(quantities_pre)
    products = []
    quantities = []
    for k in range(tot):
        if totQ > 0 and quantities_pre[k]/totQ >= 0.01:
            products.append(products_pre[k])
            quantities.append(quantities_pre[k])
    lastConsumptions = ConsumptionHistory.objects.filter(customer=user).order_by('-date')[:10]
    lastMenus = MenuHistory.objects.filter(customer=user).order_by('-date')[:10]
    return render(request, "users/profile.html", 
                {
                    "user":user,
                    "self":self,
                    "cotisations":cotisations,
                    "whitelists": whitelists,
                    "reloads": reloads,
                    "products": products,
                    "quantities": quantities,
                    "lastConsumptions": lastConsumptions,
                    "lastMenus": lastMenus,
                })

@active_required
@login_required
@permission_required('auth.add_user')
def createUser(request):
    """
    Displays a :class:`~users.forms.CreateUserForm` to create a user (:class:`django.contrib.auth.models.User`).
    """
    form = CreateUserForm(request.POST or None)
    if(form.is_valid()):
        user = form.save(commit=False)
        user.save()
        user.profile.school = form.cleaned_data['school']
        user.save()
        messages.success(request, "L'utilisateur a bien été créé")
        return redirect(reverse('users:profile', kwargs={'pk':user.pk}))
    return render(request, "form.html", {"form_entete": "Gestion des utilisateurs", "form":form, "form_title":"Création d'un nouvel utilisateur", "form_button":"Créer mon compte", "form_button_icon": "user-plus", 'extra_html': '<strong>En cliquant sur le bouton "Créer mon compte", vous :<ul><li>attestez sur l\'honneur que les informations fournies à l\'association Coopé Technopôle Metz sont correctes et que vous n\'avez jamais été enregistré dans l\'association sous un autre nom / pseudonyme</li><li>joignez l\'association de votre plein gré</li><li>vous engagez à respecter les statuts et le réglement intérieur de l\'association (envoyés par mail)</li><li>reconnaissez le but de l\'assocation Coopé Technopôle Metz et vous attestez avoir pris conaissances des droits et des devoirs des membres de l\'association</li><li>consentez à ce que les données fournies à l\'association, ainsi que vos autres données de compte (débit, crédit, solde et historique des transactions) soient stockées dans le logiciel de gestion et accessibles par tous les membres actifs de l\'association, en particulier par le comité de direction</li></ul></strong>'})

@active_required
@login_required
@permission_required('auth.view_user')
def searchUser(request):
    """
    Displays a :class:`~users.forms.SelectUserForm` to search a user (:class:`django.contrib.auth.models.User`).
    """
    form = SelectUserForm(request.POST or None)
    if(form.is_valid()):
        return redirect(reverse('users:profile', kwargs={"pk":form.cleaned_data['user'].pk}))
    return render(request, "form.html", {"form_entete": "Gestion des utilisateurs", "form": form, "form_title": "Rechercher un utilisateur", "form_button": "Afficher le profil", "form_button_icon": "search"})

@active_required
@login_required
@permission_required('auth.view_user')
def usersIndex(request):
    """
    Display the list of all users (:class:`django.contrib.auth.models.User`).
    """
    users = User.objects.all()
    return render(request, "users/users_index.html", {"users":users})

@active_required
@login_required
@permission_required('auth.change_user')
def editGroups(request, pk):
    """
    Displays a :class:`users.form.GroupsEditForm` to edit the groups of a user (:class:`django.contrib.auth.models.User`).
    """
    user = get_object_or_404(User, pk=pk)
    form = GroupsEditForm(request.POST or None, instance=user)
    if(form.is_valid()):
        form.save()
        messages.success(request, "Les groupes de l'utilisateur " + user.username + " ont bien été enregistrés.")
        return redirect(reverse('users:profile', kwargs={'pk':pk}))
    extra_css = "#id_groups{height:200px;}"
    return render(request, "form.html", {"form_entete": "Gestion de l'utilisateur " + user.username, "form": form, "form_title": "Modification des groupes", "form_button": "Enregistrer", "form_button_icon": "pencil-alt", "extra_css": extra_css})

@active_required
@login_required
@permission_required('auth.change_user')
def editPassword(request, pk):
    """
    Displays a :class:`users.form.EditPasswordForm` to edit the password of a user (:class:`django.contrib.auth.models.User`).
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
        return render(request, "form.html", {"form_entete": "Modification de mon compte", "form": form, "form_title": "Modification de mon mot de passe", "form_button": "Modifier mon mot de passe", "form_button_icon": "pencil-alt"})

@active_required
@login_required
@permission_required('auth.change_user')
def editUser(request, pk):
    """
    Displays a :class:`~users.forms.CreateUserForm` to edit a user (:class:`django.contrib.auth.models.User`).
    """
    user = get_object_or_404(User, pk=pk)
    form = CreateUserForm(request.POST or None, instance=user, initial = {'school': user.profile.school})
    if(form.is_valid()):
        user.profile.school = form.cleaned_data['school']
        user.save()
        messages.success(request, "Les modifications ont bien été enregistrées")
        return redirect(reverse('users:profile', kwargs={'pk': pk}))
    return render(request, "form.html", {"form_entete":"Modification du compte " + user.username, "form": form, "form_title": "Modification des informations", "form_button": "Modifier", "form_button_icon": "pencil-alt"})

@active_required
@login_required
@permission_required('auth.change_user')
def resetPassword(request, pk):
    """
    Reset the password of a user (:class:`django.contrib.auth.models.User`).
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
    Get requested user (:class:`django.contrib.auth.models.User`) and return username, balance and is_adherent in JSON format.

    pk
        The primary key of the user to get infos.
    """
    user = get_object_or_404(User, pk=pk)
    data = json.dumps({"username": user.username, "balance": user.profile.balance, "is_adherent": user.profile.is_adherent})
    return HttpResponse(data, content_type='application/json')

@active_required
@login_required
@self_or_has_perm('pk', 'auth.view_user')
def allReloads(request, pk, page):
    """
    Display all the :class:`reloads <gestion.models.Reload>` of the requested user (:class:`django.contrib.auth.models.User`).
    """
    user = get_object_or_404(User, pk=pk)
    allReloads = Reload.objects.filter(customer=user).order_by('-date')
    paginator = Paginator(allReloads, 10)
    reloads = paginator.get_page(page)
    return render(request, "users/allReloads.html", {"reloads": reloads, "user":user})

@active_required
@login_required
@self_or_has_perm('pk', 'auth.view_user')
def all_consumptions(request, pk, page):
    """
    Display all the `consumptions <gestion.models.ConsumptionHistory>` of the requested user (:class:`django.contrib.auth.models.User`).
    """
    user = get_object_or_404(User, pk=pk)
    all_consumptions = ConsumptionHistory.objects.filter(customer=user).order_by('-date')
    paginator = Paginator(all_consumptions, 10)
    consumptions = paginator.get_page(page)
    return render(request, "users/all_consumptions.html", {"consumptions": consumptions, "user":user})

@active_required
@login_required
@self_or_has_perm('pk', 'auth.view_user')
def all_menus(request, pk, page):
    """
    Display all the `menus <gestion.models.MenuHistory>` of the requested user (:class:`django.contrib.auth.models.User`).
    """
    user = get_object_or_404(User, pk=pk)
    all_menus = MenuHistory.objects.filter(customer=user).order_by('-date')
    paginator = Paginator(all_menus, 10)
    menus = paginator.get_page(page)
    return render(request, "users/all_menus.html", {"menus": menus, "user":user})
    
@active_required
@login_required
@permission_required('auth.change_user')
def switch_activate_user(request, pk):
    """
    Switch the active status of the requested user (:class:`django.contrib.auth.models.User`).

    pk
        The primary key of the user to switch status
    """
    user = get_object_or_404(User, pk=pk)
    user.is_active = 1 - user.is_active
    user.save()
    messages.success(request, "Le statut de l'utilisateur a bien été changé")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@active_required
@login_required
@permission_required('auth.view_user')
def gen_user_infos(request, pk):
    """
    Generates a latex document include adhesion certificate and list of `cotisations <users.models.CotisationHistory>`.
    """
    user= get_object_or_404(User, pk=pk)
    cotisations = CotisationHistory.objects.filter(user=user).order_by('-paymentDate')
    now = datetime.now()
    path = os.path.join(settings.BASE_DIR, "users/templates/users/coope.png")
    return render_to_pdf(request, 'users/bulletin.tex', {"user": user, "now": now, "cotisations": cotisations, "path":path}, filename="bulletin_" + user.first_name + "_" + user.last_name + ".pdf")

########## Groups ##########

@active_required
@login_required
@permission_required('auth.view_group')
def groupsIndex(request):
    """
    Displays all the groups (:class:`django.contrib.auth.models.Group`).
    """
    groups = Group.objects.all()
    return render(request, "users/groups_index.html", {"groups": groups})

@active_required
@login_required
@permission_required('auth.view_group')
def groupProfile(request, pk):
    """
    Displays the profile of a group (:class:`django.contrib.auth.models.Group`).
    """
    group = get_object_or_404(Group, pk=pk)
    return render(request, "users/group_profile.html", {"group": group})

@active_required
@login_required
@permission_required('auth.add_group')
def createGroup(request):
    """
    Displays a :class:`~users.forms.CreateGroupForm` to create a group (:class:`django.contrib.auth.models.Group`).
    """
    form = CreateGroupForm(request.POST or None)
    if(form.is_valid()):
        group = form.save()
        messages.success(request, "Le groupe " + form.cleaned_data['name'] + " a bien été crée.")
        return redirect(reverse('users:groupProfile', kwargs={'pk': group.pk}))
    return render(request, "form.html", {"form_entete": "Gestion des utilisateurs", "form":form, "form_title": "Création d'un groupe de droit", "form_button": "Créer le groupe de droit", "form_button_icon": "plus-square"})

@active_required
@login_required
@permission_required('auth.change_group')
def editGroup(request, pk):
    """
    Displays a :class:`~users.forms.EditGroupForm` to edit a group (:class:`django.contrib.auth.models.Group`).

    pk
        The primary key of the group to edit.
    """
    group = get_object_or_404(Group, pk=pk)
    form = EditGroupForm(request.POST or None, instance=group)
    extra_css = "#id_permissions{height:200px;}"
    if(form.is_valid()):
        form.save()
        messages.success(request, "Le groupe " + group.name + " a bien été modifié.")
        return redirect(reverse('users:groupProfile', kwargs={'pk': group.pk}))
    return render(request, "form.html", {"form_entete": "Gestion des utilisateurs", "form": form, "form_title": "Modification du groupe de droit " + group.name, "form_button": "Modifier le groupe de droit", "form_button_icon": "pencil-alt", "extra_css":extra_css})

@active_required
@login_required
@permission_required('auth.delete_group')
def deleteGroup(request, pk):
    """
    Deletes the requested group (:class:`django.contrib.auth.models.Group`).

    pk
        The primary key of the group to delete
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
    Removes a right from a given group (:class:`django.contrib.auth.models.Group`).
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
    Removes a user (:class:`django.contrib.auth.models.User`) from a given group (:class:`django.contrib.auth.models.Group`).
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
    """
    Lists the staff (:class:`django.contrib.auth.models.User` with is_staff True)
    """
    admins = User.objects.filter(is_staff=True)
    return render(request, "users/admins_index.html", {"admins": admins})

@active_required
@login_required
@admin_required
def addAdmin(request):
    """
    Displays a :class:`users.forms.SelectNonAdminUserForm` to select a non admin user (:class:`django.contrib.auth.models.User`) and add it to the admins.
    """
    form = SelectNonAdminUserForm(request.POST or None)
    if(form.is_valid()):
        user = form.cleaned_data['user']
        user.is_staff = True
        user.save()
        messages.success(request, "L'utilisateur " + user.username + " a bien été rajouté aux admins")
        return redirect(reverse('users:adminsIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Ajout d'un admin", "form_button": "Ajouter l'utilisateur aux admins", "form_button_icon": "user-plus"})

@active_required
@login_required
@admin_required
def removeAdmin(request, pk):
    """
    Removes an user (:class:`django.contrib.auth.models.User`) from staff.

    pk
        The primary key of the user (:class:`django.contrib.auth.models.User`) to remove from staff
    """
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
    """
    Lists the superusers (:class:`django.contrib.auth.models.User` with is_superuser True).
    """
    superusers = User.objects.filter(is_superuser=True)
    return render(request, "users/superusers_index.html", {"superusers": superusers})

@active_required
@login_required
@superuser_required
def addSuperuser(request):
    """
    Displays a :class:`users.forms.SelectNonAdminUserForm` to select a non superuser user (:class:`django.contrib.auth.models.User`) and add it to the superusers.
    """
    form = SelectNonSuperUserForm(request.POST or None)
    if form.is_valid():
        user = form.cleaned_data['user']
        user.is_admin = True
        user.is_superuser = True
        user.save()
        messages.success(request, "L'utilisateur " + user.username + " a bien été rajouté aux superusers")
        return redirect(reverse('users:superusersIndex'))
    return render(request, "form.html", {"form_entete": "Gestion des superusers", "form": form, "form_title": "Ajout d'un superuser", "form_button":"Ajouter l'utilisateur aux superusers", "form_button_icon": "user-plus"})

@active_required
@login_required
@superuser_required
def removeSuperuser(request, pk):
    """
    Removes a user (:class:`django.contrib.auth.models.User`) from superusers.
    """
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
    """
    Displays a :class:`users.forms.addCotisationHistoryForm` to add a :class:`Cotisation History <users.models.CotisationHistory` to the requested user (:class:`django.contrib.auth.models.User`).

    pk
        The primary key of the user to add a cotisation history
    """
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
        if(user.profile.cotisationEnd and user.profile.cotisationEnd > timezone.now()):
            cotisation.endDate = user.profile.cotisationEnd + timedelta(days=cotisation.cotisation.duration)
        else:
            cotisation.endDate = datetime.now() + timedelta(days=cotisation.cotisation.duration)
        user.profile.cotisationEnd = cotisation.endDate
        user.save()
        cotisation.save()
        messages.success(request, "La cotisation a bien été ajoutée")
        return redirect(reverse('users:profile',kwargs={'pk':user.pk}))
    return render(request, "form.html",{"form": form, "form_title": "Ajout d'une cotisation pour l'utilisateur " + str(user), "form_button": "Ajouter", "form_button_icon": "plus-square"})

@active_required
@login_required
@permission_required('users.delete_cotisationhistory')
def deleteCotisationHistory(request, pk):
    """
    Delete the requested :class:`~users.models.CotisationHistory`.

    pk
        The primary key of tthe CotisationHistory to delete.
    """
    cotisationHistory = get_object_or_404(CotisationHistory, pk=pk)
    user = cotisationHistory.user
    user.profile.cotisationEnd = user.profile.cotisationEnd - timedelta(days=cotisationHistory.duration)
    if(cotisationHistory.paymentMethod.affect_balance):
        user.profile.debit -= cotisationHistory.cotisation.amount
    user.save()
    cotisationHistory.delete()
    messages.success(request, "La cotisation a bien été supprimée")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

########## Whitelist ##########

@active_required
@login_required
@permission_required('users.add_whitelisthistory')
def addWhiteListHistory(request, pk):
    """
    Displays a :class:`users.forms.addWhiteListHistoryForm` to add a :class:`~users.models.WhiteListHistory` to the requested user (:class:`django.contrib.auth.models.User`).
    """
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
    return render(request, "form.html", {"form": form, "form_title": "Ajout d'un accès gracieux pour " + user.username, "form_button": "Ajouter", "form_button_icon": "plus-square"})

########## Schools ##########

@active_required
@login_required
@permission_required('users.view_school')
def schoolsIndex(request):
    """
    Lists the :class:`Schools <users.models.School>`.
    """
    schools = School.objects.all()
    return render(request, "users/schools_index.html", {"schools": schools})

@active_required
@login_required
@permission_required('users.add_school')
def createSchool(request):
    """
    Displays :class:`~users.forms.SchoolForm` to add a :class:`~users.models.School`.
    """
    form = SchoolForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "L'école a bien été créée")
        return redirect(reverse('users:schoolsIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Création d'une école", "form_button": "Créer", "form_button_icon": "plus-square"})

@active_required
@login_required
@permission_required('users.change_school')
def editSchool(request, pk):
    """
    Displays :class:`~users.forms.SchoolForm` to edit a :class:`~users.models.School`.

    pk
        The primary key of the school to edit.
    """
    school = get_object_or_404(School, pk=pk)
    form = SchoolForm(request.POST or None, instance=school)
    if(form.is_valid()):
        form.save()
        messages.success(request, "L'école a bien été modifiée")
        return redirect(reverse('users:schoolsIndex'))
    return render(request, "form.html", {"form": form, "form_title": "Modification de l'école " + str(school), "form_button": "Modifier", "form_button": "pencil-alt"})

@active_required
@login_required
@permission_required('users.delete_school')
def deleteSchool(request, pk):
    """
    Deletes a :class:`users.models.School`.

    pk
        The primary key of the School to delete.
    """
    school = get_object_or_404(School, pk=pk)
    message = "L'école " + str(school) + " a bien été supprimée"
    school.delete()
    messages.success(request, message)
    return redirect(reverse('users:schoolsIndex'))

########## Autocomplete searchs ##########

class AllUsersAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autcomplete for all users (:class:`django.contrib.auth.models.User`).
    """
    def get_queryset(self):
        qs = User.objects.all()
        if self.q:
            qs = qs.filter(Q(username__icontains=self.q) | Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q))
        return qs

class ActiveUsersAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete for active users (:class:`django.contrib.auth.models.User`).
    """
    def get_queryset(self):
        qs = User.objects.filter(is_active=True)
        if self.q:
            qs = qs.filter(Q(username__icontains=self.q) | Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q))
        return qs

class AdherentAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete for adherents (:class:`django.contrib.auth.models.User`).
    """
    def get_queryset(self):
        qs = User.objects.all()
        pks = [x.pk for x in qs if x.is_adherent]
        qs = User.objects.filter(pk__in=pks)
        if self.q:
            qs = qs.filter(Q(username__icontains=self.q) | Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q))
        return qs


class NonSuperUserAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete for non-superuser users (:class:`django.contrib.auth.models.User`).
    """
    def get_queryset(self):
        qs = User.objects.filter(is_superuser=False)
        if self.q:
            qs = qs.filter(Q(username__icontains=self.q) | Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q))
        return qs

class NonAdminUserAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete for non-admin users (:class:`django.contrib.auth.models.User`).
    """
    def get_queryset(self):
        qs = User.objects.filter(is_staff=False)
        if self.q:
            qs = qs.filter(Q(username__icontains=self.q) | Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q))
        return qs
