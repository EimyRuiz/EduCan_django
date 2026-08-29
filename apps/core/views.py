from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .mongo import db


class ConfiguracionView(APIView):
    def get(self, request):
        config = db.configuracion.find_one({'tipo': 'sitio'}) or {}
        config.pop('_id', None)
        config.pop('tipo', None)
        return Response(config)

    def post(self, request):
        if not isinstance(request.user, dict) or request.user.get('rol') != 'administrador':
            return Response({'error': 'No autorizado.'}, status=status.HTTP_403_FORBIDDEN)

        db.configuracion.update_one(
            {'tipo': 'sitio'},
            {'$set': request.data},
            upsert=True
        )
        return Response({'mensaje': 'Configuración actualizada.'})