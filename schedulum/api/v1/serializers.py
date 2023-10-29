import datetime

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import validate_email
from rest_framework import serializers, validators

from schedules.models import Week, Schedule


class ScheduleMixinSerializer():

    def get_related_obj(self, date):
        return Week.objects.filter(start__lte=date, end__gte=date).first()

    def exits_schedule(self, date_str, week_objects):
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
        if value.weekday() == 6:
            raise serializers.ValidationError('Воскресенье неучебный день.')
        return value

    def validate(self, attrs):
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


class ScheduleSerializer(ScheduleMixinSerializer, serializers.ModelSerializer):
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


class ScheduleUpdateSerializer(ScheduleMixinSerializer,
                               serializers.ModelSerializer):

    class Meta:
        model = Schedule
        fields = ('text', 'notes', 'repetition_rate', 'repetition_count')
