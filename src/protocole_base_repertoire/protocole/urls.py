from django.urls import path
from . import views

app_name = 'protocole'
urlpatterns = [
    path('', views.index, name='index'),
    path('simulation/', views.simulation, name='simulation'),
    path('reinitialisation_data/', views.reinitialisation_data, name='reinitialisation_data'),
    path('read_data/', views.read_data, name='read_data'),
    path('write_data/', views.write_data, name='write_data'),
]