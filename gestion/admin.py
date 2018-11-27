from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Reload, Refund, Product, Keg, ConsumptionHistory, KegHistory, Consumption, Menu, MenuHistory

admin.site.register(Reload, SimpleHistoryAdmin)
admin.site.register(Refund, SimpleHistoryAdmin)
admin.site.register(Product, SimpleHistoryAdmin)
admin.site.register(Keg, SimpleHistoryAdmin)
admin.site.register(ConsumptionHistory, SimpleHistoryAdmin)
admin.site.register(KegHistory, SimpleHistoryAdmin)
admin.site.register(Consumption, SimpleHistoryAdmin)
admin.site.register(Menu, SimpleHistoryAdmin)
admin.site.register(MenuHistory, SimpleHistoryAdmin)