from rest_framework import serializers


class ProductSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100)
    categoria = serializers.ChoiceField(choices=[
        'Collar', 'Pechera', 'Correa', 'Impermeable',
        'Juguete', 'Comida', 'Producto de aseo', 'Accesorio'
    ])
    descripcion = serializers.CharField()
    precio = serializers.FloatField()
    imagen = serializers.URLField(required=False, allow_blank=True)