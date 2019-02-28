from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import PaymentMethod, GeneralPreferences, Cotisation

class CotisationAdmin(SimpleHistoryAdmin):
    """
    The admin class for :class:`Consumptions <preferences.models.Cotisation>`.
    """
    list_display = ('__str__', 'amount', 'duration')
    ordering = ('-duration', '-amount')

class GeneralPreferencesAdmin(SimpleHistoryAdmin):
    """
    The admin class for :class:`Consumptions <preferences.models.GeneralPreferences>`.
    """
    list_display = ('is_active', 'president', 'vice_president', 'treasurer', 'secretary', 'brewer', 'grocer', 'use_pinte_monitoring', 'lost_pintes_allowed', 'floating_buttons', 'automatic_logout_time')

class PaymentMethodAdmin(SimpleHistoryAdmin):
    """
    The admin class for :class:`Consumptions <preferences.models.PaymentMethod>`.
    """
    list_display = ('name', 'is_active', 'is_usable_in_cotisation', 'is_usable_in_reload', 'affect_balance')
    ordering = ('name',)
    search_fields = ('name',)
    list_filter = ('is_active', 'is_usable_in_cotisation', 'is_usable_in_reload', 'affect_balance')

admin.site.register(PaymentMethod, PaymentMethodAdmin)
admin.site.register(GeneralPreferences, GeneralPreferencesAdmin)
admin.site.register(Cotisation, CotisationAdmin)