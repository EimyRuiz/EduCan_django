from django.shortcuts import render

# Create your views here.
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.core.mongo import db
from apps.core.authentication import IsMongoAuthenticated
from .serializers import ServiceRequestSerializer

import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage


class UploadPerroFotoView(APIView):
    permission_classes = [IsMongoAuthenticated]

    def post(self, request, pk):
        archivo = request.FILES.get('foto')
        if not archivo:
            return Response({'error': 'No se envió ninguna imagen.'}, status=status.HTTP_400_BAD_REQUEST)

        carpeta = os.path.join(settings.MEDIA_ROOT, 'perros')
        os.makedirs(carpeta, exist_ok=True)

        nombre_archivo = f"{pk}_{archivo.name}"
        fs = FileSystemStorage(location=carpeta)
        fs.save(nombre_archivo, archivo)

        url_foto = f"{settings.MEDIA_URL}perros/{nombre_archivo}"
        db.solicitudes.update_one({'_id': ObjectId(pk)}, {'$set': {'perro_foto': url_foto}})

        return Response({'mensaje': 'Foto del perro guardada.', 'foto': url_foto})


def serialize_request(doc):
    doc['id'] = str(doc['_id'])
    doc.pop('_id')
    doc['fecha_inicio'] = str(doc['fecha_inicio'])
    return doc


class ServiceRequestListCreateView(APIView):
    permission_classes = [IsMongoAuthenticated]

    def get(self, request):
        # El cliente ve solo sus solicitudes; el admin/adiestrador ven todas
        rol = request.user.get('rol')
        if rol == 'cliente':
            solicitudes = list(db.solicitudes.find({'cliente_id': request.user.get('user_id')}))
        else:
            solicitudes = list(db.solicitudes.find())
        return Response([serialize_request(s) for s in solicitudes])

    def post(self, request):
        serializer = ServiceRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        nueva_solicitud = {
            **data,
            'fecha_inicio': data['fecha_inicio'].isoformat(),
            'cliente_id': request.user.get('user_id'),
            'cliente_nombre': request.user.get('email'),
            'adiestrador_id': None,
            'estado': 'pendiente',  # pendiente | aceptada | rechazada
            'perro_foto': None,
            'creado_en': datetime.utcnow().isoformat(),
        }

        resultado = db.solicitudes.insert_one(nueva_solicitud)
        return Response(
            {'mensaje': 'Solicitud creada.', 'id': str(resultado.inserted_id)},
            status=status.HTTP_201_CREATED
        )


class ServiceRequestDetailView(APIView):
    permission_classes = [IsMongoAuthenticated]

    def get_object(self, pk):
        try:
            return db.solicitudes.find_one({'_id': ObjectId(pk)})
        except InvalidId:
            return None

    def patch(self, request, pk):
        """Usado para: asignar adiestrador, cambiar estado (aceptar/rechazar)"""
        solicitud = self.get_object(pk)
        if not solicitud:
            return Response({'error': 'No encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        campos_permitidos = {}
        if 'adiestrador_id' in request.data:
            campos_permitidos['adiestrador_id'] = request.data['adiestrador_id']
        if 'estado' in request.data:
            campos_permitidos['estado'] = request.data['estado']

        db.solicitudes.update_one({'_id': ObjectId(pk)}, {'$set': campos_permitidos})
        return Response({'mensaje': 'Solicitud actualizada.'})