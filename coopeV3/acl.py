from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from functools import wraps

from preferences.models import GeneralPreferences

def admin_required(view):
    """
    Test if the user is staff.
    """
    return user_passes_test(lambda u: u.is_staff)(view)

def superuser_required(view):
    """
    Test if the user is superuser.
    """
    return user_passes_test(lambda u: u.is_superuser)(view)

def self_or_has_perm(pkName, perm):
    """
    Test if the user is the request user (pk) or has perm permission.
    """
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            user = get_object_or_404(User, pk=kwargs[pkName])
            if(user == request.user or request.user.has_perm(perm)):
                return view(request, *args, **kwargs)
            else:
                return redirect(reverse('users:login'))
        return wrapper
    return decorator

def active_required(view):
    """
    Test if the site is active (:attr:`preferences.models.GeneralPreferences.is_active`).
    """
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
        if(not gp.is_active):
            return redirect(reverse('preferences:inactive'))
        return view(request, *args, **kwargs)
    return wrapper
    
def acl_or(*perms):
    """
    Test if a user has one of perms
    """
    def decorator(view):
        @wraps(view)
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
    """
    Test if a user has all perms
    """
    def decorator(view):
        @wraps(view)
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