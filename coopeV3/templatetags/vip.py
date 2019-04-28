from django import template
import random
from preferences.models import GeneralPreferences

register = template.Library()

@register.simple_tag
def president():
    """
    A tag which returns :attr:`preferences.models.GeneralPreferences.president`.
    """
    gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
    return gp.president

@register.simple_tag
def treasurer():
    """
    A tag which returns :attr:`preferences.models.GeneralPreferences.treasurer`.
    """
    gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
    return gp.treasurer

@register.simple_tag
def secretary():
    """
    A tag which returns :attr:`preferences.models.GeneralPreferences.secretary`.
    """
    gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
    return gp.secretary

@register.simple_tag
def phoenix():
    """
    A tag which returns :attr:`preferences.models.GeneralPreferences.phoenixTM_responsible`.
    """
    gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
    return gp.phoenixTM_responsible

@register.simple_tag
def global_message():
    """
    A tag which returns :attr:`preferences.models.GeneralPreferences.global_message`.
    """
    gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
    messages = gp.global_message.split("\n")
    return random.choice(messages)

@register.simple_tag
def logout_time():
    """
    A tag which returns :attr:`preferences.models.GeneralPreferences.automatic_logout_time`.
    """
    gp, _ = GeneralPreferences.objects.get_or_create(pk=1)
    logout_time = gp.automatic_logout_time
    return logout_time

@register.simple_tag
def statutes():
    """
    A tag which returns :attr:`preferences.models.GeneralPreferences.statutes`.
    """
    gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
    try:
        return '<a target="_blank" href="' + gp.statutes.url + '">' + str(gp.statutes) + '</a>'
    except:
        return "Pas de document"

@register.simple_tag
def rules():
    """
    A tag which returns :attr:`preferences.models.GeneralPreferences.rules`.
    """
    gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
    try:
        return '<a target="_blank" href="' + gp.rules.url + '">' + str(gp.rules) + '</a>'
    except:
        return "Pas de document"

@register.simple_tag
def menu():
    """
    A tag which returns :attr:`preferences.models.GeneralPreferences.menu`.
    """
    gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
    try:
        return '<a target="_blank" href="' + gp.menu.url + '">' + str(gp.menu) + '</a>'
    except:
        return "Pas de document"

@register.simple_tag
def alcool_charter():
    """
    A tag which returns :attr:`preferences.models.GeneralPreferences.alcool_charter`.
    """
    gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
    try:
        return '<a target="_blank" href="' + gp.alcohol_charter.url + '">' + str(gp.alcohol_charter) + '</a>'
    except:
        return "Pas de document"
