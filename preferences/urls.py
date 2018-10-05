from django.urls import path

from . import views

app_name="preferences"
urlpatterns = [
    path('generalPreferences', views.generalPreferences, name="generalPreferences"),
    path('cotisationsIndex', views.cotisationsIndex, name="cotisationsIndex"),
    path('addCotisation', views.addCotisation, name="addCotisation"),
    path('editCotisation/<int:pk>', views.editCotisation, name="editCotisation"),
    path('deleteCotisation/<int:pk>', views.deleteCotisation, name="deleteCotisation"),
    path('paymentMethodsIndex', views.paymentMethodsIndex, name="paymentMethodsIndex"),
    path('addPaymentMethod', views.addPaymentMethod, name="addPaymentMethod"),
    path('editPaymentMethod/<int:pk>', views.editPaymentMethod, name="editPaymentMethod"),
    path('deletePaymentMethod/<int:pk>', views.deletePaymentMethod, name="deletePaymentMethod"),
]
