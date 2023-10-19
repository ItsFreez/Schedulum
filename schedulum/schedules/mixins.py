import datetime

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db.models import Count

ERROR_HIGHER_OBJ_SAMPLE = 'Необходимо изначально создать "{field}".'


class GetModel():

    def get_model(self, model_name):
        return apps.get_model(app_label='schedules', model_name=model_name)


class TrueDiffInterval():

    def get_true_diff(self):
        difference = self.end - self.start
        return difference.days + 1


class ValidationMonthMixin(GetModel, TrueDiffInterval):

    def get_average_date(self):
        return self.start + datetime.timedelta(days=10)

    def get_higher_obj(self, model_name):
        model = self.get_model(model_name)
        average_date = self.get_average_date()
        return model.objects.filter(year=average_date.year).first()

    def validate_higher_obj(self, model_name):
        model = self.get_model(model_name)
        model_obj = self.get_higher_obj(model_name)
        field = model._meta.verbose_name
        if model_obj is None:
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
        model = self.get_model(self.__class__.__name__)
        start_obj = model.objects.filter(start__lte=self.start,
                                         end__gte=self.start).first()
        end_obj = model.objects.filter(start__lte=self.end,
                                       end__gte=self.end).first()
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


class ValidationWeekMixin(GetModel, TrueDiffInterval):

    def get_count_weeks(self, model_name):
        model_queryset = self.get_higher_model_queryset(model_name)
        model_obj = model_queryset.annotate(count_weeks=Count('weeks')).first()
        return model_obj.count_weeks

    def get_higher_model_queryset(self, model_name):
        model = self.get_model(model_name)
        return model.objects.filter(start__lte=self.start, end__gte=self.start)

    def get_higher_obj(self, model_name):
        return self.get_higher_model_queryset(model_name).first()

    def validate_higher_obj(self, model_name):
        model = self.get_model(model_name)
        model_obj = self.get_higher_obj(model_name)
        field = model._meta.verbose_name.title()
        if model_obj is None:
            raise ValidationError(ERROR_HIGHER_OBJ_SAMPLE.format(field=field))
        return None

    def validate_len_interval(self):
        true_diff = self.get_true_diff()
        if true_diff != 7:
            raise ValidationError('Неделя должна содержать 7 дней.')
        return None
