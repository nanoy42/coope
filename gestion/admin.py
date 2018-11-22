from django.contrib import admin

from .models import Reload, Refund, Product, Keg, ConsumptionHistory

admin.site.register(Reload)
admin.site.register(Refund)
admin.site.register(Product)
admin.site.register(Keg)
admin.site.register(ConsumptionHistory)