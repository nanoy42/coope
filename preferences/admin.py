from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import PaymentMethod, GeneralPreferences, Cotisation, DivideHistory, PriceProfile, Improvement

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
    list_display = ('is_active', 'president', 'treasurer', 'secretary', 'phoenixTM_responsible', 'use_pinte_monitoring', 'lost_pintes_allowed', 'floating_buttons', 'automatic_logout_time')

class PaymentMethodAdmin(SimpleHistoryAdmin):
    """
    The admin class for :class:`Consumptions <preferences.models.PaymentMethod>`.
    """
    list_display = ('name', 'is_active', 'is_usable_in_cotisation', 'is_usable_in_reload', 'affect_balance')
    ordering = ('name',)
    search_fields = ('name',)
    list_filter = ('is_active', 'is_usable_in_cotisation', 'is_usable_in_reload', 'affect_balance')

class PriceProfileAdmin(SimpleHistoryAdmin):
    """
    The admin class for :class:`Consumptions <preferences.models.PriceProfile>`.
    """
    list_display = ('name', 'a', 'b', 'c', 'alpha', 'use_for_draft')
    ordering = ('name',)
    search_fields = ('name',)
    list_filter = ('use_for_draft',)

class DivideHistoryAdmin(SimpleHistoryAdmin):
    """
    The admin class for Divide histories
    """
    list_display = ('date', 'total_cotisations', 'total_cotisations_amount', 'total_ptm_amount', 'coopeman')
    ordering = ('-date',)

class ImprovementAdmin(SimpleHistoryAdmin):
    """
    The admin class for Improvement.
    """
    list_display = ('title', 'mode', 'seen', 'done', 'date')
    ordering = ('-date',)
    search_fields = ('title', 'description')
    list_filter = ('mode', 'seen', 'done')

admin.site.register(PaymentMethod, PaymentMethodAdmin)
admin.site.register(GeneralPreferences, GeneralPreferencesAdmin)
admin.site.register(Cotisation, CotisationAdmin)
admin.site.register(PriceProfile, PriceProfileAdmin)
admin.site.register(DivideHistory, DivideHistoryAdmin)
admin.site.register(Improvement, ImprovementAdmin)