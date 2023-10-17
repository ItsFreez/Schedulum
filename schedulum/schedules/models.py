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
        average_date = self.start_month + datetime.timedelta(days=15)
        year = Year.objects.get(year=average_date.year)
        title = RUSSIAN_MONTHS[average_date.month]
        if Month.objects.filter(title=title, year=year).first() is not None:
            raise ValidationError('Данный месяц уже существует.')
        return super().clean()

    def save(self, *args, **kwargs):
        average_date = self.start_month + datetime.timedelta(days=15)
        self.year = Year.objects.get(year=average_date.year)
        self.title = RUSSIAN_MONTHS[average_date.month]
        return super().save(*args, **kwargs)
