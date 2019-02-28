from django.contrib import admin
from django.contrib.auth.models import Permission
from simple_history.admin import SimpleHistoryAdmin
from django.db.models import F

from .models import School, Profile, CotisationHistory, WhiteListHistory

class CotisationHistoryAdmin(SimpleHistoryAdmin):
    """
    The admin class for :class:`Consumptions <users.models.CotisationHistory>`.
    """
    list_display = ('user', 'amount', 'duration', 'paymentDate', 'endDate', 'paymentMethod')
    ordering = ('user', 'amount', 'duration', 'paymentDate', 'endDate')
    search_fields = ('user',)
    list_filter = ('paymentMethod', )

class BalanceFilter(admin.SimpleListFilter):
    """
    A filter which filters according to the sign of the balance
    """
    title = 'Solde'
    parameter_name = 'solde'

    def lookups(self, request, model_admin):
        return (
            ('po', '>0'),
            ('nu', '=0'),
            ('ne', '<0'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'po':
            return queryset.filter(credit__gt=F('debit'))
        elif self.value() == 'nu':
            return queryset.filter(credit=F('debit'))
        elif self.value() == 'ne':
            return queryset.filter(credit__lt=F('debit'))


class ProfileAdmin(SimpleHistoryAdmin):
    """
    The admin class for :class:`Consumptions <users.models.Profile>`.
    """
    list_display = ('user', 'credit', 'debit', 'balance', 'school', 'cotisationEnd', 'is_adherent')
    ordering = ('user', '-credit', '-debit')
    search_fields = ('user',)
    list_filter = ('school', BalanceFilter)

class WhiteListHistoryAdmin(SimpleHistoryAdmin):
    """
    The admin class for :class:`Consumptions <users.models.WhiteListHistory>`.
    """
    list_display = ('user', 'paymentDate', 'endDate', 'duration')
    ordering = ('user', 'duration', 'paymentDate', 'endDate')
    search_fields = ('user',)

admin.site.register(Permission, SimpleHistoryAdmin)
admin.site.register(School, SimpleHistoryAdmin)
admin.site.register(WhiteListHistory, WhiteListHistoryAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(CotisationHistory, CotisationHistoryAdmin)