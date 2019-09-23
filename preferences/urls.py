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
    path('priceProfilesIndex', views.price_profiles_index, name="priceProfilesIndex"),
    path('addPriceProfile', views.add_price_profile, name="addPriceProfile"),
    path('editPriceProfile/<int:pk>', views.edit_price_profile, name="editPriceProfile"),
    path('deletePriceProfile/<int:pk>', views.delete_price_profile, name="deletePriceProfile"),
    path('inactive', views.inactive, name="inactive"),
    path('getConfig', views.get_config, name="getConfig"),
    path('getCotisation/<int:pk>', views.get_cotisation, name="getCotisation"),
    path('addImprovement', views.add_improvement, name="addImprovement"),
    path('improvementsIndex', views.improvements_index, name="improvementsIndex"),
    path('improvementProfile/<int:pk>', views.improvement_profile, name="improvementProfile"),
    path('deleteImprovement/<int:pk>', views.delete_improvement, name="deleteImprovement"),
    path('changeImprovementState/<int:pk>', views.change_improvement_state, name="changeImprovementState"),
]
