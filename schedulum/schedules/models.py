import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.db import models

from schedules.validators import (right_end_month, right_start_month,
                                  right_year, validate_len_interval)

RUSSIAN_MONTHS = {
    1: 'Январь',
    2: 'Февраль',
    3: 'Март',
    4: 'Апрель',
    5: 'Май',
    6: 'Июнь',
    7: 'Июль',
    8: 'Август',
    9: 'Сентябрь',
    10: 'Октябрь',
    11: 'Ноябрь',
    12: 'Декабрь'
}


class Year(models.Model):
    title = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='Заголовок',
        help_text='Это поле автоматически заполнится, оставьте пустым.'
    )
    year = models.SmallIntegerField(
        validators=[MinValueValidator(settings.CURRENT_YEAR),
                    MaxValueValidator(settings.NEXT_YEAR)],
        verbose_name='Год',
        help_text=(
            'Можно указать только текущий и следующий год. Обязательное поле.'
        )
    )

    class Meta:
        verbose_name = 'год'
        verbose_name_plural = 'Годы'
        ordering = ('year',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.title = str(self.year) + ' год'
        return super().save(*args, **kwargs)


class Month(models.Model):
    title = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Заголовок',
        help_text='Это поле автоматически заполнится, оставьте пустым.'
    )
    year = models.ForeignKey(
        Year,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='Год',
        related_name='months',
        help_text='Это поле автоматически заполнится, оставьте пустым.'
    )
    start_month = models.DateField(
        validators=[right_start_month, right_year],
        verbose_name='Начало учебного месяца',
        help_text='Выберите начало учебного месяца (понедельник).'
    )
    end_month = models.DateField(
        validators=[right_end_month, right_year],
        verbose_name='Конец учебного месяца',
        help_text='Выберите конец учебного месяца (воскресенье).'
    )

    class Meta:
        verbose_name = 'месяц'
        verbose_name_plural = 'Месяцы'
        ordering = ('start_month',)
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'year',),
                name='unique_title_year',
            ),
        )

    def __str__(self):
        return self.title

    def clean(self):
        validate_len_interval(self.start_month, self.end_month)
        error_month_sample = ('Значение {field} попадает в интервал '
                              'другого месяца.')
        start_month_obj = Month.objects.filter(
            start_month__lte=self.start_month,
            end_month__gte=self.start_month
        ).first()
        end_month_obj = Month.objects.filter(
            start_month__lte=self.end_month,
            end_month__gte=self.end_month
        ).first()
        fields = ('start_month', 'end_month')
        objects = (start_month_obj, end_month_obj)
        zipped = zip(fields, objects)
        if start_month_obj is not None or end_month_obj is not None:
            error_message = [error_month_sample.format(field=field) for field,
                             object in zipped if object is not None]
            raise ValidationError(error_message)
        return super().clean()

    def save(self, *args, **kwargs):
        average_date = self.start_month + datetime.timedelta(days=15)
        self.year = Year.objects.get(year=average_date.year)
        self.title = RUSSIAN_MONTHS[average_date.month]
        return super().save(*args, **kwargs)
