from django.urls import path

from . import views

app_name="gestion"
urlpatterns = [
    path('manage', views.manage, name="manage"),
]
