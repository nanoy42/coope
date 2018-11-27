from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import PaymentMethod, GeneralPreferences, Cotisation

admin.site.register(PaymentMethod, SimpleHistoryAdmin)
admin.site.register(GeneralPreferences, SimpleHistoryAdmin)
admin.site.register(Cotisation, SimpleHistoryAdmin)