from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.services, name='services'),
    path('shop/', views.shop, name='shop'),
    path('admin-panel/', views.admin_panel, name='admin-panel'),
]