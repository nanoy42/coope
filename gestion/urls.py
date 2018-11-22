from django.urls import path

from . import views

app_name="gestion"
urlpatterns = [
    path('manage', views.manage, name="manage"),
    path('reload', views.reload, name="reload"),
    path('refund', views.refund, name="refund"),
    path('productsIndex', views.productsIndex, name="productsIndex"),
    path('productsList', views.productsList, name="productsList"),
    path('addProduct', views.addProduct, name="addProduct"),
    path('addKeg', views.addKeg, name="addKeg"),
    path('addMenu', views.addMenu, name="addMenu"),
    path('getProduct/<str:barcode>', views.getProduct, name="getProduct"),
    path('order', views.order, name="order"),
    path('ranking', views.ranking, name="ranking"),
    path('annualRanking', views.annualRanking, name="annualRanking"),
    path('searchProduct', views.searchProduct, name="searchProduct"),
    path('productProfile/<int:pk>', views.productProfile, name="productProfile"),
    path('products-autocomplete', views.ProductsAutocomplete.as_view(), name="products-autocomplete"),
]