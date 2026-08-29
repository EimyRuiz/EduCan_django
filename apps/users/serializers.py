from rest_framework import serializers


class UserRegisterSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100)
    apellido = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    telefono = serializers.CharField(max_length=20)
    ciudad = serializers.CharField(max_length=100, required=False, default='')
    password = serializers.CharField(min_length=6, write_only=True)
    rol = serializers.ChoiceField(choices=['cliente', 'adiestrador'], default='cliente')

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)