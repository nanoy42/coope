from django.contrib import admin

from .models import PaymentMethod, GeneralPreferences, Cotisation

admin.site.register(PaymentMethod)
admin.site.register(GeneralPreferences)
admin.site.register(Cotisation)
# Register your models here.
