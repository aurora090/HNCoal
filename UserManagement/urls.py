from django.urls import path
from UserManagement import views
urlpatterns = [
     path('login',views.login),
]