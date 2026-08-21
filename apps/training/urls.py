from django.urls import path
from .views import ServiceListCreateView, ServiceDetailView

urlpatterns = [
    path('', ServiceListCreateView.as_view(), name='service-list'),
    path('<str:pk>/', ServiceDetailView.as_view(), name='service-detail'),
]