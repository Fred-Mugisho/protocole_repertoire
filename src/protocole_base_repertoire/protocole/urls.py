from django.urls import path
from . import views

app_name = 'protocole'
urlpatterns = [
    path('', views.index, name='index'),
    path('simulation/', views.simulation, name='simulation'),
    path('reinitialisation_data/', views.reinitialisation_data, name='reinitialisation_data'),
]