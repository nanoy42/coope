from django.urls import path, include

from . import views

app_name="users"
urlpatterns = [
    path('login', views.loginView, name="login"),
    path('logout', views.logoutView, name="logout"),
    path('index', views.index, name="index"),
    path('profile/<int:pk>', views.profile, name="profile"),
    path('createUser', views.createUser, name="createUser"),
    path('searchUser', views.searchUser, name="searchUser"),
    path('usersIndex', views.usersIndex, name="usersIndex"),
    path('editGroups/<int:pk>', views.editGroups, name="editGroups"),
    path('editPassword/<int:pk>', views.editPassword, name="editPassword"),
    path('editUser/<int:pk>', views.editUser, name="editUser"),
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
    path('all-users-autocomplete', views.AllUsersAutocomplete.as_view(), name="all-users-autocomplete"),
    path('active-users-autcocomplete', views.ActiveUsersAutocomplete.as_view(), name="active-users-autocomplete"),
    path('non-super-users-autocomplete', views.NonSuperUserAutocomplete.as_view(), name="non-super-users-autocomplete"),
    path('non-admin-users-autocomplete', views.NonAdminUserAutocomplete.as_view(), name="non-admin-users-autocomplete"),
    path('getUser/<int:pk>', views.getUser, name="getUser"),
    path('addCotisationHistory/<int:pk>', views.addCotisationHistory, name="addCotisationHistory"),
    path('deleteCotisationHistory/<int:pk>', views.deleteCotisationHistory, name="deleteCotisationHistory"),
    path('addWhiteListHistory/<int:pk>', views.addWhiteListHistory, name="addWhiteListHistory"),
    path('schoolsIndex', views.schoolsIndex, name="schoolsIndex"),
    path('createSchool', views.createSchool, name="createSchool"),
    path('editSchool/<int:pk>', views.editSchool, name="editSchool"),
    path('deleteSchool/<int:pk>', views.deleteSchool, name="deleteSchool"),
    path('allReloads/<int:pk>/<int:page>', views.allReloads, name="allReloads"),
    path('allConsumptions/<int:pk>/<int:page>', views.all_consumptions, name="allConsumptions"),
    path('allMenus/<int:pk>/<int:page>', views.all_menus, name="allMenus"),
    path('exportCSV', views.export_csv, name="exportCSV"),
    path('switchActivateUser/<int:pk>', views.switch_activate_user, name="switchActivateUser"),
    path('genUserInfos/<int:pk>', views.gen_user_infos, name="genUserInfos"),
    path('addBanishmentHistory/<int:pk>', views.addBanishmentHistory, name="addBanishmentHistory"),
]
