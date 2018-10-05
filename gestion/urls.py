from django.urls import path

from . import views

app_name="gestion"
urlpatterns = [
    path('manage', views.manage, name="manage"),
    path('reload', views.reload, name="reload"),
    path('refund', views.refund, name="refund"),
    path('productsIndex', views.productsIndex, name="productsIndex"),
    path('addProduct', views.addProduct, name="addProduct"),
    path('addKeg', views.addKeg, name="addKeg"),
    path('addMenu', views.addMenu, name="addMenu"),
    path('getProduct/<str:barcode>', views.getProduct, name="getProduct"),
]
