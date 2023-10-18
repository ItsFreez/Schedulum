import datetime as dt

from django.apps import apps
from django.core.exceptions import ValidationError
from django.conf import settings

INVALID_PAST_ERROR = 'Август и Июль неучебные месяцы.'


def right_start(date):
    if date < dt.date(year=settings.CURRENT_YEAR,
                      month=settings.CURRENT_MONTH,
                      day=1):
        raise ValidationError('Прошедший месяц не доступен для выбора.')
    if (settings.CURRENT_JULY < date < settings.CURRENT_AUGUST
            or settings.NEXT_JULY < date < settings.NEXT_AUGUST):
        raise ValidationError(INVALID_PAST_ERROR)
    return date


def right_end(date):
    if (date.month == 8
            or (settings.CURRENT_START_JULY < date
                < settings.CURRENT_END_AUGUST or settings.NEXT_START_JULY
                < date < settings.NEXT_END_AUGUST)):
        raise ValidationError(INVALID_PAST_ERROR)
    return date


def right_year(date):
    if date.year < settings.CURRENT_YEAR or date.year > settings.NEXT_YEAR:
        raise ValidationError('Выберите текущий или следующий год.')
    return date


def validate_len_interval(model_name, start, end):
    if end <= start:
        raise ValidationError('Начало интервала не может быть позже конца.')
    difference = end - start
    true_diff = difference.days + 1
    count_weeks = true_diff // 7
    if model_name == 'Month':
        if count_weeks < 4 or count_weeks > 5:
            raise ValidationError('Интервал должен содержать 4 или 5 недель.')
        if true_diff % 7 != 0:
            raise ValidationError('Все недели в указанном интервале должны '
                                  'содержать 7 дней.')
    if model_name == 'Week' and true_diff != 7:
        raise ValidationError('Неделя должна содержать 7 дней.')
    return None


def validate_exist_interval(model_name, start, end):
    error_sample = 'Значение "{field}" попадает в интервал другого объекта.'
    model = apps.get_model(app_label='schedules', model_name=model_name)
    start_obj = model.objects.filter(
        start__lte=start,
        end__gte=start
    ).first()
    end_obj = model.objects.filter(
        start__lte=end,
        end__gte=end
    ).first()
    fields = (model._meta.get_field('start').verbose_name,
              model._meta.get_field('end').verbose_name)
    objects = (start_obj, end_obj)
    zipped = zip(fields, objects)
    if start_obj is not None or end_obj is not None:
        error_message = [error_sample.format(field=field) for field,
                         object in zipped if object is not None]
        raise ValidationError(error_message)


def validate_month_obj(model_name, value):
    model = apps.get_model(app_label='schedules', model_name=model_name)
    model_obj = model.objects.filter(
            start__lte=value,
            end__gte=value
    ).first()
    if model_obj is None:
        raise ValidationError('Необходимо изначально создать месяц.')
    return model_obj
