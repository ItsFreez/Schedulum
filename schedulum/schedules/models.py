from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from schedules.mixins import (
    ValidationMonthMixin, ValidationMonthAndWeekIntervalMixin,
    ValidationWeekMixin
)
from schedules.validators import correct_end, correct_start

User = get_user_model()
RUSSIAN_MONTHS = settings.RUSSIAN_MONTHS


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

    def clean(self):
        if Year.objects.filter(year=self.year).first() is not None:
            raise ValidationError('Такой год уже существует.')
        return super().clean()

    def save(self, *args, **kwargs):
        self.title = str(self.year) + ' год'
        return super().save(*args, **kwargs)


class Month(ValidationMonthMixin, ValidationMonthAndWeekIntervalMixin,
            models.Model):
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
        validators=[correct_start],
        verbose_name='Начало учебного месяца',
        help_text='Выберите начало учебного месяца (понедельник).'
    )
    end = models.DateField(
        validators=[correct_end],
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
        self.validate_related_obj()
        self.validate_interval()
        self.validate_len_interval()
        return super().clean()

    def save(self, *args, **kwargs):
        self.year = self.get_related_obj()
        self.title = RUSSIAN_MONTHS[self.get_average_date().month]
        return super().save(*args, **kwargs)


class Week(ValidationMonthAndWeekIntervalMixin, ValidationWeekMixin,
           models.Model):
    title = models.CharField(
        max_length=10,
        verbose_name='Заголовок',
        help_text='Укажите название и номер недели.'
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
        validators=[correct_start],
        verbose_name='Начало учебной недели',
        help_text='Выберите начало учебной недели (понедельник).'
    )
    end = models.DateField(
        validators=[correct_end],
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
        return f'{self.title} {self.month.title}'

    def clean(self):
        self.validate_related_obj()
        self.validate_interval()
        self.validate_len_interval()
        return super().clean()

    def save(self, *args, **kwargs):
        self.month = self.get_related_obj()
        return super().save(*args, **kwargs)


class Schedule(models.Model):
    text = models.TextField(
        max_length=500,
        verbose_name='Расписание пар',
        help_text='Обязательное. Укажите время, название и аудиторию пары.'
    )
    additionally_text = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Заметок',
        help_text='Необязательное. Можно написать заметки для себя.'
    )
    date = models.DateField(
        verbose_name='Дата',
        help_text='Обязательное. Выберите дату для расписания.'
    )
