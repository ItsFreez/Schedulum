import datetime

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import validate_email
from rest_framework import serializers, validators

from schedules.models import Week, Schedule


class ScheduleMixinSerializer():
    """Миксин для сериализатора Schedule."""

    def get_related_obj(self, date):
        """Получение объекта related модели по полям start и end."""
        return Week.objects.filter(start__lte=date, end__gte=date).first()

    def exits_schedule(self, date_str, week_objects):
        """Проверка попадания расписания в даты другого объекта расписания."""
        user = self.context['request'].user
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        current_schedule = Schedule.objects.filter(
            date=date, author=user
        ).first()
        for week_obj in week_objects:
            schedule_objs = Schedule.objects.filter(
                author=user, week=week_obj)
            for schedule in schedule_objs:
                if (schedule.date.weekday() == date.weekday()
                        and schedule != current_schedule):
                    raise serializers.ValidationError(
                        'Ваше расписание попадает на день другого расписания. '
                        'Или повтор совпадает с другим расписанием.'
                    )
        return None

    def get_related_week_objects(self, date_str, rate=False, count=False):
        """
        Получение списка всех объектов Week, указанных при помощи даты
        и повторений.
        """
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        week_objects = []
        if rate and count:
            for repeat in range(1, count + 1):
                new_date = date + datetime.timedelta(
                    days=((7 * rate) * repeat)
                )
                week_obj = self.get_related_obj(new_date)
                week_objects.append(week_obj)
        basic_week_obj = self.get_related_obj(date)
        week_objects.append(basic_week_obj)
        return week_objects

    def validate_date(self, value):
        """Проверка попадания даты на воскресенье."""
        if value.weekday() == 6:
            raise serializers.ValidationError('Воскресенье неучебный день.')
        return value

    def validate(self, attrs):
        """
        1. Проверка на заполнение полей rate и count;
        2. Проверка наличия необходимого объекта related модели;
        3. Запуск проверки попадания расписания в даты другого расписания.
        """
        date = self.initial_data.get('date')
        if date is None:
            date = self.instance.date
            date = date.strftime('%Y-%m-%d')
        rate = self.initial_data.get('repetition_rate')
        count = self.initial_data.get('repetition_count')
        repetition_list = [rate, count]
        if any(repetition_list) and not all(repetition_list):
            raise serializers.ValidationError(
                'При назначении повторения должны быть указаны количество и '
                'частота.'
            )
        week_objects = self.get_related_week_objects(date, rate, count)
        if None in week_objects:
            raise serializers.ValidationError(
                'Вы пытаетесь добавить или повторить расписание на '
                'несуществующую неделю.'
            )
        self.exits_schedule(date, week_objects)
        return attrs


class RegistrationSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя и получения кода."""

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
    """Сериализатор для получения авторизационного токена."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class ScheduleSerializer(ScheduleMixinSerializer, serializers.ModelSerializer):
    """Сериализатор для модели Schedule."""

    text = serializers.CharField(max_length=500)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Schedule
        exclude = ('id', 'week')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Schedule.objects.all(),
                fields=('date', 'author'),
                message=('У вас уже существует расписание на эту дату.')
            )
        ]


class ScheduleDaySerializer(serializers.ModelSerializer):
    """Сериализатор для получения расписания на определенный день."""

    class Meta:
        model = Schedule
        fields = ('text', 'notes')


class ScheduleUpdateSerializer(ScheduleMixinSerializer,
                               serializers.ModelSerializer):
    """Сериализатор для метода 'UPDATE' модели Schedule."""

    class Meta:
        model = Schedule
        fields = ('text', 'notes', 'repetition_rate', 'repetition_count')
