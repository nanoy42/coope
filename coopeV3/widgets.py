from django.forms.widgets import Select, Input
from django.template import Context, Template
from django.template.loader import get_template

class SearchField(Input):

    def render(self, name, value, attrs=None):
        #super().render(name, value, attrs)
        template = get_template('search_field.html')
        context = Context({})
        return template.render(context)
