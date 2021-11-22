from django.urls import path
from Applications.Landing import views

urlpatterns = [
    path('', views.hello_world, name='hello_world'),
]