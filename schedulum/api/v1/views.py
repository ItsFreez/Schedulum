import datetime

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import AccessToken

from api.v1.serializers import (RegistrationSerializer,
                                TokenObtainAccessSerializer,
                                ScheduleSerializer, ScheduleDaySerializer,
                                ScheduleUpdateSerializer)
from schedules.models import Month, Week, Schedule, Year, User

ERROR_SAMPLE = 'Пользователь с заданным {field} уже существует!'


class BaseScheduleViewSet(mixins.RetrieveModelMixin,
                          mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          GenericViewSet):
    """Миксин ViewSet для CRUD Schedule."""

    pass


@api_view(['POST'])
@permission_classes((AllowAny,))
def registration(request):
    """View-функция регистрации пользователей и получения кода."""
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
    """View-функция для получения авторизационного токена."""
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


class ScheduleViewSet(BaseScheduleViewSet):
    """ViewSet для модели Schedule."""

    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_field = 'date'
    lookup_url_kwarg = 'date'

    def get_object(self):
        """Получение объекта по полям date и author."""
        queryset = self.filter_queryset(self.get_queryset())
        date_str = self.kwargs.get(self.lookup_url_kwarg)
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        filter_kwargs = {self.lookup_field: date,
                         'author': self.request.user}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        """Получение класса сериализатора в зависимости от метода запроса."""
        if self.request.method in ['PATCH']:
            return ScheduleUpdateSerializer
        return super().get_serializer_class()

    def get_schedule(self, date):
        """Получение объекта Schedule по полям author и date."""
        week = Week.objects.filter(start__lte=date, end__gte=date).first()
        schedule = Schedule.objects.filter(
            date__week_day=date.weekday() + 2,
            author=self.request.user,
            week=week,
        ).first()
        return schedule

    @action(
        methods=['GET'],
        detail=False,
        url_path='today',
        serializer_class=ScheduleDaySerializer
    )
    def get_actual_schedule(self, request):
        """Получение и передача объекта Schedule на сегодняшний день."""
        date = settings.CURRENT_DAY
        schedule_obj = self.get_schedule(date)
        serializer = self.get_serializer(schedule_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['GET'],
        detail=False,
        url_path='tomorrow',
        serializer_class=ScheduleDaySerializer
    )
    def get_tomorrow_schedule(self, request):
        """Получение и передача объекта Schedule на завтрашний день."""
        date = settings.NEXT_DAY
        schedule_obj = self.get_schedule(date)
        serializer = self.get_serializer(schedule_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WeekView(APIView):

    def get(self, request, *args, **kwargs):
        """Получение и передача всех объектов Schedule на нужную неделю."""
        year = get_object_or_404(Year, year=kwargs['year'])
        month = get_object_or_404(Month, title=kwargs['month'], year=year)
        week_number = kwargs['week_num']
        week_title = 'Неделя ' + str(week_number)
        week = get_object_or_404(Week, title=week_title, month=month)
        schedules = {}
        for number in range(7):
            date = week.start + datetime.timedelta(days=number)
            schedule = Schedule.objects.filter(
                date__week_day=date.weekday() + 2,
                author=request.user,
                week=week
            ).first()
            date = date.strftime('%Y-%m-%d')
            if schedule is None:
                schedules[date] = ''
            else:
                schedules[date] = {'text': schedule.text,
                                   'notes': schedule.notes}
        return Response(schedules, status=status.HTTP_200_OK)
