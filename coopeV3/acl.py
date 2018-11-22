from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

from preferences.models import GeneralPreferences

def admin_required(view):
    """
    Test if the user is staff
    """
    return user_passes_test(view, lambda u:u.is_staff)

def superuser_required(view):
    """
    Test if the user is superuser
    """
    return user_passes_test(view, lambda u:u.is_superuser)

def self_or_has_perm(pkName, perm):
    """
    Test if the user is the request user (pk) or has perm permission
    """
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            user = get_object_or_404(User, pk=kwargs[pkName])
            if(user == request.user or request.user.has_perm(perm)):
                return view(request, *args, **kwargs)
            else:
                return redirect(reverse('users:login'))
        return wrapper
    return decorator

def active_required(view):
    def wrapper(request, *args, **kwargs):
        gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
        if(not gp.is_active):
            return redirect(reverse('preferences:inactif'))
        return view(request, *args, **kwargs)
    return wrapper
    
def acl_or(*perms):
    def decorator(view):
        def wrapper(request,*args, **kwargs):
            can_pass = request.user.has_perm(perms[0])
            for perm in perms:
                can_pass = can_pass or request.user.has_perm(perm)
            if can_pass:
                return view(request, *args, **kwargs)
            else:
                return redirect(reverse('users:login'))
        return wrapper
    return decorator

def acl_and(*perms):
    def decorator(view):
        def wrapper(request,*args, **kwargs):
            can_pass = request.user.has_perm(perms[0])
            for perm in perms:
                can_pass = can_pass and request.user.has_perm(perm)
            if can_pass:
                return view(request, *args, **kwargs)
            else:
                return redirect(reverse('users:login'))
        return wrapper
    return decorator