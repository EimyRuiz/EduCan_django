from django.shortcuts import render

# Create your views here.
from bson import ObjectId
from bson.errors import InvalidId
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.core.mongo import db
from .serializers import ServiceSerializer


def serialize_doc(doc):
    doc['id'] = str(doc['_id'])
    doc.pop('_id')
    return doc


class ServiceListCreateView(APIView):
    def get(self, request):
        servicios = list(db.servicios.find())
        return Response([serialize_doc(s) for s in servicios])

    def post(self, request):
        serializer = ServiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resultado = db.servicios.insert_one(serializer.validated_data)
        return Response(
            {'mensaje': 'Servicio creado.', 'id': str(resultado.inserted_id)},
            status=status.HTTP_201_CREATED
        )


class ServiceDetailView(APIView):
    def get_object(self, pk):
        try:
            return db.servicios.find_one({'_id': ObjectId(pk)})
        except InvalidId:
            return None

    def get(self, request, pk):
        servicio = self.get_object(pk)
        if not servicio:
            return Response({'error': 'No encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serialize_doc(servicio))

    def put(self, request, pk):
        servicio = self.get_object(pk)
        if not servicio:
            return Response({'error': 'No encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ServiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        db.servicios.update_one({'_id': ObjectId(pk)}, {'$set': serializer.validated_data})
        return Response({'mensaje': 'Servicio actualizado.'})

    def delete(self, request, pk):
        servicio = self.get_object(pk)
        if not servicio:
            return Response({'error': 'No encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        db.servicios.delete_one({'_id': ObjectId(pk)})
        return Response({'mensaje': 'Servicio eliminado.'}, status=status.HTTP_204_NO_CONTENT)