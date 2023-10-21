import locale

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from schedules.mixins import (
    MonthMixin, ValidationMonthAndWeekIntervalMixin,
    ScheduleMixin, WeekMixin
)
from schedules.validators import (correct_end, correct_start,
                                  validate_sunday)

locale.setlocale(category=locale.LC_ALL, locale="Russian")
User = get_user_model()
RATE_CHOICES = (
    (1, 'Каждую неделю'),
    (2, 'Раз в 2 недели'),
    (3, 'Раз в 3 недели'),
    (4, 'Раз в 4 недели'),
)
COUNT_CHOICES = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
    (7, 7),
    (8, 8),
    (9, 9),
    (10, 10),
)


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


class Month(MonthMixin, ValidationMonthAndWeekIntervalMixin, models.Model):
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
            models.UniqueConstraint(
                fields=('start', 'end',),
                name='unique_start_end_month',
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
        self.title = self.get_average_date().strftime('%B')
        return super().save(*args, **kwargs)


class Week(ValidationMonthAndWeekIntervalMixin, WeekMixin, models.Model):
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
            models.UniqueConstraint(
                fields=('start', 'end',),
                name='unique_start_end_week',
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


class Schedule(ScheduleMixin, models.Model):
    text = models.TextField(
        max_length=500,
        verbose_name='Расписание пар',
        help_text='Обязательное. Укажите время, название и аудиторию пары.'
    )
    additionally_text = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Заметки',
        help_text='Необязательное. Можно написать заметки для себя.'
    )
    date = models.DateField(
        validators=[validate_sunday],
        verbose_name='Дата',
        help_text='Обязательное. Выберите дату для расписания.'
    )
    repetition_rate = models.SmallIntegerField(
        blank=True,
        null=True,
        choices=RATE_CHOICES,
        verbose_name='Частота повторения',
        help_text='Необязательно. Выберите как часто будет повторяться.'
    )
    repetition_count = models.SmallIntegerField(
        blank=True,
        null=True,
        choices=COUNT_CHOICES,
        verbose_name='Количество повторений',
        help_text='Необязательное. Выберите сколько раз будет повторяться.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор расписания',
        help_text='Обязательное. Выберите автора.'
    )
    week = models.ManyToManyField(
        Week,
        blank=True,
        editable=False,
        verbose_name='Недели',
    )

    class Meta:
        default_related_name = 'schedules'
        verbose_name = 'расписание'
        verbose_name_plural = 'Расписания'
        ordering = ('date', 'author',)
        constraints = (
            models.UniqueConstraint(
                fields=('date', 'author',),
                name='unique_date_author',
            ),
        )

    def __str__(self):
        str_date = self.date.strftime('%d %B %Y')
        return f'{str_date} {self.author.username}'

    def clean(self):
        self.validate_exist_week(self.date)
        self.validate_empty_repetition()
        return super().clean()

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
