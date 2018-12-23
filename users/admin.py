from django.contrib import admin
from django.contrib.auth.models import Permission
from simple_history.admin import SimpleHistoryAdmin

from .models import School, Profile, CotisationHistory

class ProfileAdmin(SimpleHistoryAdmin):
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

admin.site.register(Permission, SimpleHistoryAdmin)
admin.site.register(School, SimpleHistoryAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(CotisationHistory, SimpleHistoryAdmin)