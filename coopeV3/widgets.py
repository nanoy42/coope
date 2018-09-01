from django.forms.widgets import Input
from django.template import Context, Template
from django.template.loader import get_template

class SearchField:
    def __init__(self, url):
        self.url = url

    def render(self, name, value, attrs=None):
        super().render(name, value, attrs)
        template = get_template('search_field.html')
        context = Context({})
        return template.render(context)
