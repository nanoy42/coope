from django.shortcuts import redirect
from django.urls import reverse

def home(request):
    if request.user is not None:
        if(request.user.has_perm('gestion.can_manage')):
            return redirect(reverse('gestion:manage'))
        else:
            return redirect(reverse('users:profile', kwargs={'pk': request.user.pk}))
    else:
        return redirect(reverse('users:login'))
