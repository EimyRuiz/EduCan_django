from django.shortcuts import render

# Create your views here.
import bcrypt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken 
from bson import ObjectId

from apps.core.authentication import IsMongoAuthenticated

from apps.core.mongo import db
from .serializers import UserRegisterSerializer, UserLoginSerializer

#register view
class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Verifica que el email no esté ya registrado
        if db.usuarios.find_one({'email': data['email']}):
            return Response(
                {'error': 'Ya existe un usuario con ese email.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Hashea la contraseña antes de guardarla
        password_hash = bcrypt.hashpw(
            data['password'].encode('utf-8'),
            bcrypt.gensalt()
        )

        nuevo_usuario = {
            'nombre': data['nombre'],
            'apellido': data['apellido'],
            'email': data['email'],
            'telefono': data['telefono'],
            'ciudad': data.get('ciudad', ''),
            'password': password_hash.decode('utf-8'),
            'rol': data['rol'],
        }

        resultado = db.usuarios.insert_one(nuevo_usuario)

        return Response(
            {
                'mensaje': 'Usuario registrado correctamente.',
                'id': str(resultado.inserted_id),
            },
            status=status.HTTP_201_CREATED
        )





# login view 

class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        usuario = db.usuarios.find_one({'email': data['email']})

        if not usuario:
            return Response(
                {'error': 'Email o contraseña incorrectos.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        password_valida = bcrypt.checkpw(
            data['password'].encode('utf-8'),
            usuario['password'].encode('utf-8')
        )

        if not password_valida:
            return Response(
                {'error': 'Email o contraseña incorrectos.'},
                status=status.HTTP_401_UNAUTHORIZED
            )


            # Genera el token manualmente, con los datos de este usuario de Mongo
        refresh = RefreshToken()
        refresh['user_id'] = str(usuario['_id'])
        refresh['email'] = usuario['email']
        refresh['rol'] = usuario['rol']

        return Response(
            {
                'mensaje': 'Login exitoso.',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'usuario': {
                    'id': str(usuario['_id']),
                    'nombre': usuario['nombre'],
                    'email': usuario['email'],
                    'rol': usuario['rol'],
                }
            },
            status=status.HTTP_200_OK
        )
    


    # autenticacion de prueba

class MeView(APIView):
    permission_classes = [IsMongoAuthenticated]

    def get(self, request):
        user_id = request.user.get('user_id')
        usuario = db.usuarios.find_one({'_id': ObjectId(user_id)})

        return Response({
            'id': str(usuario['_id']),
            'nombre': usuario['nombre'],
            'email': usuario['email'],
            'rol': usuario['rol'],
        })


# panel admin view
class UserListView(APIView):
    permission_classes = [IsMongoAuthenticated]

    def get(self, request):
        if request.user.get('rol') != 'administrador':
            return Response({'error': 'No autorizado.'}, status=status.HTTP_403_FORBIDDEN)

        usuarios = list(db.usuarios.find())
        for u in usuarios:
            u['id'] = str(u['_id'])
            u.pop('_id')
            u.pop('password', None)
        return Response(usuarios)