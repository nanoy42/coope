from django.contrib import admin

from .models import School, Profile, CotisationHistory

admin.site.register(School)
admin.site.register(Profile)
admin.site.register(CotisationHistory)
# Register your models here.
