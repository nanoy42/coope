from django.contrib import admin
from django.contrib.auth.models import Permission
from simple_history.admin import SimpleHistoryAdmin

from .models import School, Profile, CotisationHistory

admin.site.register(Permission, SimpleHistoryAdmin)
admin.site.register(School, SimpleHistoryAdmin)
admin.site.register(Profile, SimpleHistoryAdmin)
admin.site.register(CotisationHistory, SimpleHistoryAdmin)