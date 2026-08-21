from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.permissions import BasePermission


class MongoJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        return validated_token.payload

    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except (InvalidToken, TokenError):
            return None

class IsMongoAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, dict)