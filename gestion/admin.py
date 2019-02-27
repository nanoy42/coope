from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Reload, Refund, Product, Keg, ConsumptionHistory, KegHistory, Consumption, Menu, MenuHistory

class ConsumptionAdmin(SimpleHistoryAdmin):
    list_display = ('customer', 'product', 'quantity')
    ordering = ('-quantity', )
    search_fields = ('customer', 'product')

class ConsumptionHistoryAdmin(SimpleHistoryAdmin):
    list_display = ('customer', 'product', 'quantity', 'paymentMethod', 'date', 'amount')
    ordering = ('-date', )
    search_fields = ('customer', 'product')
    list_filter = ('paymentMethod',)

class KegAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'stockHold', 'capacity', 'is_active')
    ordering = ('name', )
    search_fields = ('name',)
    list_filter = ('capacity', 'is_active')

class KegHistoryAdmin(SimpleHistoryAdmin):
    list_display = ('keg', 'openingDate', 'closingDate', 'isCurrentKegHistory', 'quantitySold')
    ordering = ('-openingDate', 'quantitySold')
    search_fields = ('keg',)
    list_filter = ('isCurrentKegHistory', 'keg')

class MenuHistoryAdmin(SimpleHistoryAdmin):
    list_display = ('customer', 'menu', 'paymentMethod', 'date', 'quantity', 'amount')
    ordering = ('-date',)
    search_fields = ('customer', 'menu')

class MenuAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'amount', 'is_active')
    ordering = ('name', 'amount')
    search_fields = ('name',)
    list_filter = ('is_active', )

class ProductAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'amount', 'is_active', 'category', 'adherentRequired', 'stockHold', 'stockBar', 'volume', 'deg')
    ordering = ('name', 'amount', 'stockHold', 'stockBar', 'deg')
    search_fields = ('name',)
    list_filter = ('is_active', 'adherentRequired', 'category')

class ReloadAdmin(SimpleHistoryAdmin):
    list_display = ('customer', 'amount', 'date', 'PaymentMethod')
    ordering = ('-date', 'amount', 'customer')
    search_fields = ('customer',)
    list_filter = ('PaymentMethod', )

class RefundAdmin(SimpleHistoryAdmin):
    list_display = ('customer', 'amount', 'date')
    ordering = ('-date', 'amount', 'customer')
    search_fields = ('customer',)

admin.site.register(Reload, ReloadAdmin)
admin.site.register(Refund, RefundAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Keg, KegAdmin)
admin.site.register(ConsumptionHistory, ConsumptionHistoryAdmin)
admin.site.register(KegHistory, KegHistoryAdmin)
admin.site.register(Consumption, ConsumptionAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(MenuHistory, MenuHistoryAdmin)