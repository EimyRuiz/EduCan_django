from django.shortcuts import render

# Create your views here.
import bcrypt

import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
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

        if db.usuarios.find_one({'email': data['email']}):
            return Response(
                {'error': 'Ya existe un usuario con ese email.'},
                status=status.HTTP_400_BAD_REQUEST
            )

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

        # Si se registra como adiestrador, queda pendiente de aprobación
        if data['rol'] == 'adiestrador':
            nuevo_usuario['estado_aprobacion'] = 'pendiente'
            nuevo_usuario['certificado'] = None
            nuevo_usuario['especialidades_solicitadas'] = data.get('especialidades_solicitadas', [])
            nuevo_usuario['especialidades'] = []  # se llenan solo si el admin aprueba
        else:
            nuevo_usuario['estado_aprobacion'] = 'aprobado'

        resultado = db.usuarios.insert_one(nuevo_usuario)

        return Response(
            {
                'mensaje': 'Usuario registrado correctamente.',
                'id': str(resultado.inserted_id),
                'rol': data['rol'],
                'estado_aprobacion': nuevo_usuario['estado_aprobacion'],
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
    

#Endpoint para subir la foto
class UploadPhotoView(APIView):
    permission_classes = [IsMongoAuthenticated]

    def post(self, request):
        archivo = request.FILES.get('foto')
        if not archivo:
            return Response({'error': 'No se envió ninguna imagen.'}, status=status.HTTP_400_BAD_REQUEST)

        user_id = request.user.get('user_id')
        carpeta = os.path.join(settings.MEDIA_ROOT, 'perfiles')
        os.makedirs(carpeta, exist_ok=True)

        nombre_archivo = f"{user_id}_{archivo.name}"
        fs = FileSystemStorage(location=carpeta)
        fs.save(nombre_archivo, archivo)

        url_foto = f"{settings.MEDIA_URL}perfiles/{nombre_archivo}"
        db.usuarios.update_one({'_id': ObjectId(user_id)}, {'$set': {'foto': url_foto}})

        return Response({'mensaje': 'Foto actualizada.', 'foto': url_foto})



#Endpoint para subir el certificado de adiestrador
class UploadCertificadoView(APIView):
    permission_classes = [IsMongoAuthenticated]

    def post(self, request):
        archivo = request.FILES.get('certificado')
        if not archivo:
            return Response({'error': 'No se envió ningún archivo.'}, status=status.HTTP_400_BAD_REQUEST)

        user_id = request.user.get('user_id')
        carpeta = os.path.join(settings.MEDIA_ROOT, 'certificados')
        os.makedirs(carpeta, exist_ok=True)

        nombre_archivo = f"{user_id}_{archivo.name}"
        fs = FileSystemStorage(location=carpeta)
        fs.save(nombre_archivo, archivo)

        url_certificado = f"{settings.MEDIA_URL}certificados/{nombre_archivo}"
        db.usuarios.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'certificado': url_certificado}}
        )

        return Response({'mensaje': 'Certificado subido. Queda pendiente de revisión.', 'certificado': url_certificado})



#Endpoint para aprobar o rechazar adiestradores
class AprobarAdiestradorView(APIView):
    permission_classes = [IsMongoAuthenticated]

    def post(self, request, pk):
        if request.user.get('rol') != 'administrador':
            return Response({'error': 'No autorizado.'}, status=status.HTTP_403_FORBIDDEN)

        accion = request.data.get('accion')
        usuario = db.usuarios.find_one({'_id': ObjectId(pk)})

        actualizacion = {'estado_aprobacion': 'aprobado' if accion == 'aprobar' else 'rechazado'}
        if accion == 'aprobar':
            actualizacion['especialidades'] = usuario.get('especialidades_solicitadas', [])

        db.usuarios.update_one({'_id': ObjectId(pk)}, {'$set': actualizacion})
        return Response({'mensaje': f'Adiestrador {actualizacion["estado_aprobacion"]}.'})