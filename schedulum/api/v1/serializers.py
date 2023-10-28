from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import validate_email
from rest_framework import serializers


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=(UnicodeUsernameValidator(),)
    )
    email = serializers.EmailField(
        required=True,
        max_length=150,
        validators=(validate_email,)
    )
    password = serializers.CharField(required=True, max_length=128)


class TokenObtainAccessSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)
