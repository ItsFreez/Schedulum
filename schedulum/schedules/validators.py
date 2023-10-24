import datetime as dt

from django.core.exceptions import ValidationError
from django.conf import settings

CURRENT_MONTH = settings.CURRENT_MONTH
CURRENT_YEAR = settings.CURRENT_YEAR
DATES = settings.VALIDATE_DATES
INVALID_PAST_ERROR = 'Август и Июль неучебные месяцы.'


def correct_start(date):
    correct_month = dt.date(year=CURRENT_YEAR, month=CURRENT_MONTH, day=1)
    if date < correct_month:
        raise ValidationError('Прошедший месяц не доступен для выбора.')
    if (DATES['CURRENT_JULY'] < date < DATES['CURRENT_AUGUST']
            or DATES['NEXT_JULY'] < date < DATES['NEXT_AUGUST']):
        raise ValidationError(INVALID_PAST_ERROR)
    if date.weekday() != 0:
        raise ValidationError('Промежуток должен начинаться с понедельника.')
    return date


def correct_end(date):
    if (DATES['CURRENT_START_JULY'] < date < DATES['CURRENT_END_AUGUST']
            or DATES['NEXT_START_JULY'] < date < DATES['NEXT_END_AUGUST']):
        raise ValidationError(INVALID_PAST_ERROR)
    if date.weekday() != 6:
        raise ValidationError('Промежуток должен заканчиваться в воскресенье.')
    return date
