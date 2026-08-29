from django.urls import path
from .views import (RegisterView, LoginView, MeView, UserListView,UploadPhotoView, UploadCertificadoView, AprobarAdiestradorView)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', MeView.as_view(), name='me'),
    path('list/', UserListView.as_view(), name='user-list'),
    path('upload-photo/', UploadPhotoView.as_view(), name='upload-photo'),
    path('upload-certificado/', UploadCertificadoView.as_view(), name='upload-certificado'),
    path('aprobar/<str:pk>/', AprobarAdiestradorView.as_view(), name='aprobar-adiestrador'),
]