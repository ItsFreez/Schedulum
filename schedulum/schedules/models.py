import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.db import models

from schedules.validators import (
    right_end, right_start, right_year, validate_len_interval,
    validate_month_obj, validate_exist_interval
)

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
    start = models.DateField(
        validators=[right_start, right_year],
        verbose_name='Начало учебного месяца',
        help_text='Выберите начало учебного месяца (понедельник).'
    )
    end = models.DateField(
        validators=[right_end, right_year],
        verbose_name='Конец учебного месяца',
        help_text='Выберите конец учебного месяца (воскресенье).'
    )

    class Meta:
        verbose_name = 'месяц'
        verbose_name_plural = 'Месяцы'
        ordering = ('start',)
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'year',),
                name='unique_title_year',
            ),
        )

    def __str__(self):
        return f'{self.title} {self.year.title}'

    def clean(self):
        validate_len_interval(self.__class__.__name__, self.start, self.end)
        validate_exist_interval(self.__class__.__name__, self.start, self.end)
        return super().clean()

    def save(self, *args, **kwargs):
        average_date = self.start + datetime.timedelta(days=15)
        self.year, _ = Year.objects.get_or_create(year=average_date.year)
        self.title = RUSSIAN_MONTHS[average_date.month]
        return super().save(*args, **kwargs)


class Week(models.Model):
    title = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Заголовок',
        help_text=('Если создаете неделю самостоятельно обязательно укажите '
                   'название и номер недели.')
    )
    month = models.ForeignKey(
        Month,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='Месяц',
        related_name='weeks',
        help_text='Это поле автоматически заполнится, оставьте пустым.'
    )
    start = models.DateField(
        validators=[right_start, right_year],
        verbose_name='Начало учебной недели',
        help_text='Выберите начало учебной недели (понедельник).'
    )
    end = models.DateField(
        validators=[right_end, right_year],
        verbose_name='Конец учебной недели',
        help_text='Выберите конец учебной недели (воскресенье).'
    )

    class Meta:
        verbose_name = 'неделя'
        verbose_name_plural = 'Недели'
        ordering = ('start',)
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'month',),
                name='unique_title_month',
            ),
        )

    def __str__(self):
        return self.title

    def clean(self):
        validate_month_obj(Month.__name__, self.start)
        validate_len_interval(self.__class__.__name__, self.start, self.end)
        validate_exist_interval(self.__class__.__name__, self.start, self.end)
        return super().clean()

    def save(self, *args, **kwargs):
        self.month = validate_month_obj(Month.__name__, self.start)
        return super().save(*args, **kwargs)
