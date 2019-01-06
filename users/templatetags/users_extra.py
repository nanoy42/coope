import random

from django import template

register = template.Library()

@register.simple_tag
def random_filter(a, b):
    return random.randint(a, b)
