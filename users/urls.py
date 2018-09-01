from django.urls import path
from . import views

app_name="users"
urlpatterns = [
    path('login', views.loginView, name="login"),
    path('logout', views.logoutView, name="logout"),
    path('index', views.index, name="index"),
    path('profile/<int:pk>', views.profile, name="profile"),
    path('createUser', views.createUser, name="createUser"),
    path('groupsIndex', views.groupsIndex, name="groupsIndex"),
    path('groupProfile/<int:pk>', views.groupProfile, name="groupProfile"),
    path('createGroup', views.createGroup, name="createGroup"),
    path('editGroup/<int:pk>', views.editGroup, name="editGroup"),
    path('deleteGroup/<int:pk>', views.deleteGroup, name="deleteGroup"),
    path('removeRight/<int:groupPk>/<int:permissionPk>', views.removeRight, name="removeRight"),
    path('removeUser/<int:groupPk>/<int:userPk>', views.removeUser, name="removeUser"),
    path('adminsIndex', views.adminsIndex, name="adminsIndex"),
    path('addAdmin', views.addAdmin, name="addAdmin"),
    path('removeAdmin/<int:pk>', views.removeAdmin, name="removeAdmin"),
    path('superusersIndex', views.superusersIndex, name="superusersIndex"),
    path('addSuperuser', views.addSuperuser, name="addSuperuser"),
    path('removeSuperuser/<int:pk>', views.removeSuperuser, name="removeSuperuser"),
]
