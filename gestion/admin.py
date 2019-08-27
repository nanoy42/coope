from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Reload, Refund, Product, Keg, ConsumptionHistory, KegHistory, Consumption, Menu, MenuHistory, Category

class ConsumptionAdmin(SimpleHistoryAdmin):
    """
    The admin class for :class:`Consumptions <gestion.models.Consumption>`.
    """
    list_display = ('customer', 'product', 'quantity')
    ordering = ('-quantity', )
    search_fields = ('customer', 'product')

class ConsumptionHistoryAdmin(SimpleHistoryAdmin):
    """
    The admin class for :class:`Consumption Histories <gestion.models.ConsumptionHistory>`.
    """
    list_display = ('customer', 'product', 'quantity', 'paymentMethod', 'date', 'amount')
    ordering = ('-date', )
    search_fields = ('customer__username', 'customer__first_name', 'customer__last_name', 'product__name')
    list_filter = ('paymentMethod',)

class KegAdmin(SimpleHistoryAdmin):
    """
    The admin class for :class:`Kegs <gestion.models.Keg>`.
    """
    list_display = ('name', 'stockHold', 'capacity', 'is_active')
    ordering = ('name', )
    search_fields = ('name',)
    list_filter = ('capacity', 'is_active')

class KegHistoryAdmin(SimpleHistoryAdmin):
    """
    The admin class for :class:`Keg Histories <gestion.models.KegHistory>`.
    """
    list_display = ('keg', 'openingDate', 'closingDate', 'isCurrentKegHistory', 'quantitySold')
    ordering = ('-openingDate', 'quantitySold')
    search_fields = ('keg__name',)
    list_filter = ('isCurrentKegHistory', 'keg')

class MenuHistoryAdmin(SimpleHistoryAdmin):
    """
    The admin class for :class:`Menu Histories <gestion.models.MenuHistory>`.
    """
    list_display = ('customer', 'menu', 'paymentMethod', 'date', 'quantity', 'amount')
    ordering = ('-date',)
    search_fields = ('customer', 'menu')

class MenuAdmin(SimpleHistoryAdmin):
    """
    The admin class for :class:`Menu <gestion.models.Menu>`.
    """
    list_display = ('name', 'amount', 'is_active')
    ordering = ('name', 'amount')
    search_fields = ('name',)
    list_filter = ('is_active', )

class ProductAdmin(SimpleHistoryAdmin):
    """
    The admin class for :class:`Products <gestion.models.Product>`.
    """
    list_display = ('name', 'amount', 'is_active', 'category', 'adherentRequired', 'stock', 'volume', 'deg')
    ordering = ('name', 'amount', 'stock', 'deg')
    search_fields = ('name',)
    list_filter = ('is_active', 'adherentRequired', 'category')

class ReloadAdmin(SimpleHistoryAdmin):
    """
    The admin class for :class:`Reloads <gestion.models.Reload>`.
    """
    list_display = ('customer', 'amount', 'date', 'PaymentMethod')
    ordering = ('-date', 'amount', 'customer')
    search_fields = ('customer__username', 'customer__first_name', 'customer__last_name')
    list_filter = ('PaymentMethod', )

class RefundAdmin(SimpleHistoryAdmin):
    """
    The admin class for :class:`Refunds <gestion.models.Refund>`.
    """
    list_display = ('customer', 'amount', 'date')
    ordering = ('-date', 'amount', 'customer')
    search_fields = ('customer__username', 'customer__first_name', 'customer__last_name')

class CategoryAdmin(SimpleHistoryAdmin):
    """
    The admin class for Category
    """
    ordering = ("order",)

admin.site.register(Reload, ReloadAdmin)
admin.site.register(Refund, RefundAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Keg, KegAdmin)
admin.site.register(ConsumptionHistory, ConsumptionHistoryAdmin)
admin.site.register(KegHistory, KegHistoryAdmin)
admin.site.register(Consumption, ConsumptionAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(MenuHistory, MenuHistoryAdmin)
admin.site.register(Category, CategoryAdmin)