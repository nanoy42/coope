from django.contrib import admin
from django.contrib.auth.models import Permission

from .models import School, Profile, CotisationHistory

admin.site.register(Permission)
admin.site.register(School)
admin.site.register(Profile)
admin.site.register(CotisationHistory)