import datetime

from django.apps import apps
from django.core.exceptions import ValidationError

ERROR_HIGHER_OBJ_SAMPLE = 'Необходимо изначально создать "{field}".'


class GetModel():

    def get_model(self):
        return apps.get_model(app_label='schedules',
                              model_name=self.__class__.__name__)


class TrueDiffInterval():

    def get_true_diff(self):
        difference = self.end - self.start
        return difference.days + 1


class MonthMixin(GetModel, TrueDiffInterval):

    def get_average_date(self):
        return self.start + datetime.timedelta(days=15)

    def get_related_model(self):
        model = self.get_model()
        return model._meta.get_field('year').related_model

    def get_related_obj(self):
        model = self.get_related_model()
        average_date = self.get_average_date()
        return model.objects.filter(year=average_date.year).first()

    def validate_related_obj(self):
        related_model_obj = self.get_related_obj()
        field = self.get_related_model()._meta.verbose_name.title()
        if related_model_obj is None:
            raise ValidationError(ERROR_HIGHER_OBJ_SAMPLE.format(field=field))
        return None

    def validate_len_interval(self):
        true_diff = self.get_true_diff()
        count_weeks = true_diff // 7
        if true_diff % 7 != 0:
            raise ValidationError('Все недели в указанном интервале должны '
                                  'содержать 7 дней.')
        if count_weeks < 4 or count_weeks > 5:
            raise ValidationError('Интервал должен содержать 4 или 5 недель.')
        return None


class ValidationMonthAndWeekIntervalMixin(GetModel):

    def validate_interval(self):
        self.validate_incorrect_interval()
        self.validate_exist_interval()
        return None

    def validate_exist_interval(self):
        error_sample = 'Значение "{field}" попадает в другой интервал.'
        model = self.get_model()
        start_obj = model.objects.filter(start__lt=self.start,
                                         end__gt=self.start).first()
        end_obj = model.objects.filter(start__lt=self.end,
                                       end__gt=self.end).first()
        fields = (model._meta.get_field('start').verbose_name,
                  model._meta.get_field('end').verbose_name)
        objects = (start_obj, end_obj)
        zipped = zip(fields, objects)
        if start_obj is not None or end_obj is not None:
            error_message = [error_sample.format(field=field) for field,
                             object in zipped if object is not None]
            raise ValidationError(error_message)
        return None

    def validate_incorrect_interval(self):
        if self.start >= self.end:
            raise ValidationError(
                'Конец интервала должен быть позже его начала.'
            )
        return None


class ScheduleMixin(GetModel):

    def get_related_model(self):
        model = self.get_model()
        return model._meta.get_field('week').related_model

    def get_related_obj(self, date):
        model = self.get_related_model()
        return model.objects.filter(start__lte=date, end__gte=date).first()

    def get_related_week_objects(self):
        week_objects = []
        if self.repetition_rate and self.repetition_count:
            for repeat in range(1, self.repetition_count + 1):
                new_date = self.date + datetime.timedelta(
                    days=((7 * self.repetition_rate) * repeat)
                )
                week_obj = self.get_related_obj(new_date)
                week_objects.append(week_obj)
        basic_week_obj = self.get_related_obj(self.date)
        week_objects.append(basic_week_obj)
        return week_objects

    def validate_empty_repetition(self):
        repetition_list = [self.repetition_rate, self.repetition_count]
        if any(repetition_list) and not all(repetition_list):
            raise ValidationError('При назначении повторения должны быть '
                                  'указаны количество и частота.')
        return None

    def validate_exist_schedule(self):
        model = self.get_model()
        current_schedule = model.objects.filter(date=self.date,
                                                author=self.author).first()
        for week_obj in self.get_related_week_objects():
            schedule_objs = model.objects.filter(author=self.author,
                                                 week=week_obj)
            for schedule in schedule_objs:
                if (schedule.date.weekday() == self.date.weekday()
                        and schedule != current_schedule):
                    raise ValidationError(
                        'Ваше расписание попадает на день другого расписания. '
                        'Или повтор совпадает с другим расписанием.'
                    )
        return None

    def validate_exist_weeks(self):
        week_objs = self.get_related_week_objects()
        if None in week_objs:
            raise ValidationError('Вы пытаетесь добавить или повторить '
                                  'расписание на несуществующую неделю.')
        return None


class WeekMixin(GetModel, TrueDiffInterval):

    def get_related_model(self):
        model = self.get_model()
        return model._meta.get_field('month').related_model

    def get_related_obj(self):
        model = self.get_related_model()
        return model.objects.filter(start__lte=self.start,
                                    end__gte=self.start).first()

    def validate_related_obj(self):
        related_model_obj = self.get_related_obj()
        field = self.get_related_model()._meta.verbose_name.title()
        if related_model_obj is None:
            raise ValidationError(ERROR_HIGHER_OBJ_SAMPLE.format(field=field))
        return None

    def validate_len_interval(self):
        true_diff = self.get_true_diff()
        if true_diff != 7:
            raise ValidationError('Неделя должна содержать 7 дней.')
        return None
