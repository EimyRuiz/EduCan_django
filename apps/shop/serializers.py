from rest_framework import serializers


class ProductSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100)
    descripcion = serializers.CharField()
    precio = serializers.FloatField()
    imagen = serializers.URLField(required=False, allow_blank=True)
    categoria = serializers.CharField(max_length=50, required=False, default='general')
    stock = serializers.IntegerField(required=False, default=0)