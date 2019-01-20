from django import template
import random
from preferences.models import GeneralPreferences

register = template.Library()

@register.simple_tag
def president():
    gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
    return gp.president

@register.simple_tag
def vice_president():
    gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
    return gp.vice_president

@register.simple_tag
def treasurer():
    gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
    return gp.treasurer

@register.simple_tag
def secretary():
    gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
    return gp.secretary

@register.simple_tag
def brewer():
    gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
    return gp.brewer

@register.simple_tag
def grocer():
    gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
    return gp.grocer

@register.simple_tag
def global_message():
    gp,_ = GeneralPreferences.objects.get_or_create(pk=1)
    messages = gp.global_message.split("\n")
    return random.choice(messages)

@register.simple_tag
def logout_time():
    gp, _ = GeneralPreferences.objects.get_or_create(pk=1)
    logout_time = gp.automatic_logout_time
    return logout_time