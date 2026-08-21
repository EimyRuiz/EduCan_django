from django.shortcuts import render
from apps.core.mongo import db
# Create your views here.
def home(request):
    return render(request, 'pages/home.html')


def services(request):
    servicios = list(db.servicios.find())
    return render(request, 'pages/services.html', {'servicios': servicios})


def shop(request):
    productos = list(db.productos.find())
    return render(request, 'pages/shop.html', {'productos': productos})


def admin_panel(request):
    return render(request, 'pages/admin_panel.html')