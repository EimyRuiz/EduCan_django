from django.shortcuts import render

# Create your views here.
from bson import ObjectId
from bson.errors import InvalidId
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.core.mongo import db
from .serializers import ProductSerializer


def serialize_doc(doc):
    doc['id'] = str(doc['_id'])
    doc.pop('_id')
    return doc


class ProductListCreateView(APIView):
    def get(self, request):
        productos = list(db.productos.find())
        return Response([serialize_doc(p) for p in productos])

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resultado = db.productos.insert_one(serializer.validated_data)
        return Response(
            {'mensaje': 'Producto creado.', 'id': str(resultado.inserted_id)},
            status=status.HTTP_201_CREATED
        )


class ProductDetailView(APIView):
    def get_object(self, pk):
        try:
            return db.productos.find_one({'_id': ObjectId(pk)})
        except InvalidId:
            return None

    def get(self, request, pk):
        producto = self.get_object(pk)
        if not producto:
            return Response({'error': 'No encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serialize_doc(producto))

    def put(self, request, pk):
        producto = self.get_object(pk)
        if not producto:
            return Response({'error': 'No encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        db.productos.update_one({'_id': ObjectId(pk)}, {'$set': serializer.validated_data})
        return Response({'mensaje': 'Producto actualizado.'})

    def delete(self, request, pk):
        producto = self.get_object(pk)
        if not producto:
            return Response({'error': 'No encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        db.productos.delete_one({'_id': ObjectId(pk)})
        return Response({'mensaje': 'Producto eliminado.'}, status=status.HTTP_204_NO_CONTENT)