from rest_framework import serializers


class ServiceRequestSerializer(serializers.Serializer):
    # Datos del servicio
    servicio = serializers.CharField(max_length=100)
    duracion = serializers.ChoiceField(choices=[
        'corto',      # menos de 1 mes
        'mediano',    # 1 a 6 meses
        'largo',      # 6 meses a 1 año
        'muy_largo',  # más de 1 año
    ])
    fecha_inicio = serializers.DateField()

    # Datos del can
    perro_nombre = serializers.CharField(max_length=100)
    perro_raza = serializers.CharField(max_length=100)
    perro_edad = serializers.IntegerField()
    perro_peso = serializers.FloatField()
    perro_sexo = serializers.ChoiceField(choices=['macho', 'hembra'])
    perro_esterilizado = serializers.BooleanField()
    perro_vacunas_al_dia = serializers.BooleanField()
    perro_conducta = serializers.CharField(allow_blank=True, required=False)
    perro_salud = serializers.CharField(allow_blank=True, required=False)