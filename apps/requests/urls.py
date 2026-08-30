from django.urls import path
from .views import ServiceRequestListCreateView, ServiceRequestDetailView, UploadPerroFotoView

urlpatterns = [
    path('', ServiceRequestListCreateView.as_view(), name='request-list'),
    path('<str:pk>/', ServiceRequestDetailView.as_view(), name='request-detail'),
    path('<str:pk>/foto/', UploadPerroFotoView.as_view(), name='request-foto'),
]