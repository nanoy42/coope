from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .forms import CreateUserForm, LoginForm, CreateGroupForm, EditGroupForm, SelectUserForm

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

def profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    self = request.user == user
    return render(request, "users/profile.html", {"user":user, "self":self})

def createUser(request):
    form = CreateUserForm(request.POST or None)
    if(form.is_valid()):
        user = form.save(commit=False)
        user.set_password(user.username)
        user.save()
        user.profile.school = form.cleaned_data['school']
        user.save()
    return render(request, "form.html", {"form_entete": "Gestion des utilisateurs", "form":form, "form_title":"Création d'un nouvel utilisateur", "form_button":"Créer l'utilisateur"})


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
    form = SelectUserForm(request.POST or None, restrictTo="non-admins")
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
    form = SelectUserForm(request.POST or None, restrictTo="non-superusers")
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
