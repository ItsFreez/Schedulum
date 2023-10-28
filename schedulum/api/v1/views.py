from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.v1.serializers import (RegistrationSerializer,
                                TokenObtainAccessSerializer)
from schedules.models import User

ERROR_SAMPLE = 'Пользователь с заданным {field} уже существует!'


@api_view(['POST'])
@permission_classes((AllowAny,))
def registration(request):
    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    email_obj = User.objects.filter(email=email).first()
    username_obj = User.objects.filter(username=username).first()
    if email_obj != username_obj:
        fields = ('username', 'email')
        objects = (username_obj, email_obj)
        zipped = zip(fields, objects)
        error_message = {
            field: [ERROR_SAMPLE.format(field=field)]
            for field, object in zipped if object is not None
        }
        return Response(
            error_message,
            status=status.HTTP_400_BAD_REQUEST
        )
    user_obj = User.objects.filter(username=username, email=email).first()
    if user_obj is not None and not user_obj.check_password(password):
        return Response(
            {'password': ['Указан неверный пароль!']},
            status=status.HTTP_400_BAD_REQUEST
        )
    elif user_obj is None:
        user_obj = User.objects.create(
            username=username,
            email=email
        )
        user_obj.set_password(password)
        user_obj.save()
    confirmation_code = default_token_generator.make_token(user_obj)
    message = {'confirmation_code': str(confirmation_code)}
    return Response(message, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny,))
def get_token(request):
    serializer = TokenObtainAccessSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']
    user = get_object_or_404(User, username=username)
    if not default_token_generator.check_token(user, confirmation_code):
        return Response(
            {'confirmation_code': ['Неверный код подтверждения!']},
            status=status.HTTP_400_BAD_REQUEST
        )
    access_token = AccessToken.for_user(user)
    return Response(
        {'token': str(access_token)},
        status=status.HTTP_200_OK
    )
