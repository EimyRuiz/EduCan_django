from django.shortcuts import render
from apps.core.mongo import db
# Create your views here.
def home(request):
    servicios = list(db.servicios.find().limit(4))
    productos = list(db.productos.find().limit(3))
    return render(request, 'pages/home.html', {
        'servicios': servicios,
        'productos': productos,
    })


def services(request):
    servicios = list(db.servicios.find())
    return render(request, 'pages/services.html', {'servicios': servicios})


def shop(request):
    productos = list(db.productos.find())
    return render(request, 'pages/shop.html', {'productos': productos})


def admin_panel(request):
    return render(request, 'pages/admin_panel.html')


def request_service(request):
    return render(request, 'pages/request_service.html')