import datetime as dt

from django.core.exceptions import ValidationError
from django.conf import settings

INVALID_MONTH_ERROR = 'Выберите учебный месяц.'


def right_start_month(date):
    if date < dt.date(year=settings.CURRENT_YEAR,
                      month=settings.CURRENT_MONTH,
                      day=1):
        raise ValidationError('Прошедший месяц не доступен для выбора.')
    if (settings.CURRENT_JULY < date < settings.CURRENT_AUGUST
            or settings.NEXT_JULY < date < settings.NEXT_AUGUST):
        raise ValidationError(INVALID_MONTH_ERROR)
    return date


def right_end_month(date):
    if date.month == 8 or date.month == 7:
        raise ValidationError(INVALID_MONTH_ERROR)
    return date


def right_year(date):
    if date.year < settings.CURRENT_YEAR or date.year > settings.NEXT_YEAR:
        raise ValidationError('Выберите текущий или следующий год.')
    return date


def validate_len_interval(start, end):
    sum_start = (start.month * 30) + start.day + start.year
    sum_end = (end.month * 30) + end.day + end.year
    difference = sum_end - sum_start
    if difference > 38:
        raise ValidationError('Указан слишком длинный промежуток.')
    elif difference < 28:
        raise ValidationError('Указан слишком короткий промежуток.')
    return None
