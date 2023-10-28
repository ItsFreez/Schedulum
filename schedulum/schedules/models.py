import locale

from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from schedules.mixins import (
    MonthMixin, ValidationMonthAndWeekIntervalMixin,
    ScheduleMixin, WeekMixin
)
from schedules.validators import correct_end, correct_start

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
    """
    Модель года для администратора. Содержит два поля - заголовок и год:
    1. Заголовок формируется автоматически из указанного значения в поле год;
    2. Установлено ограничение на создание только текущего и следующего года.
    """

    title = models.CharField(
        max_length=15,
        blank=True,
        editable=False,
        verbose_name='Заголовок',
    )
    year = models.SmallIntegerField(
        validators=[MinValueValidator(settings.CURRENT_YEAR),
                    MaxValueValidator(settings.NEXT_YEAR)],
        unique=True,
        error_messages={'unique': 'Такой год уже существует.'},
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


class Month(MonthMixin, ValidationMonthAndWeekIntervalMixin, models.Model):
    """
    Модель месяца для администратора. Содержит четыре поля - заголовок,
    год (foreignkey), начало и конец учебного месяца:
    1. Заголовок и год заполняются автоматически из значений
    начала и конца месяца;
    2. Установлены ограничения на выбор дат: нельзя создать объект прошлого
    месяца, Июля или Августа, а также объект, если нет соответствующего объекта
    модели Year;
    3. Установлены два Unique Constraint: заголовок и год,
    начало и конец месяца.
    """

    title = models.CharField(
        max_length=10,
        blank=True,
        editable=False,
        verbose_name='Заголовок',
    )
    year = models.ForeignKey(
        Year,
        blank=True,
        editable=False,
        on_delete=models.CASCADE,
        verbose_name='Год',
        related_name='months',
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
        super().clean_fields()
        self.validate_related_obj()
        self.validate_interval()
        self.validate_len_interval()
        return super().clean()

    def clean_fields(self, exclude):
        return None

    def save(self, *args, **kwargs):
        self.year = self.get_related_obj()
        self.title = self.get_average_date().strftime('%B')
        return super().save(*args, **kwargs)


class Week(ValidationMonthAndWeekIntervalMixin, WeekMixin, models.Model):
    """
    Модель недели для администратора. Содержит четыре поля - заголовок,
    месяц (foreignkey), начало и конец учебной недели:
    1. Недели создаются автоматически при создании месяца, но при
    необходимости администратор может редактировать их;
    2. Месяц заполняется автоматически из значений
    начала и конца недели;
    3. Установлено ограничение на выбор дат: нельзя создать объект недели если
    нет соответствующего объекта модели Month.
    4. Установлены два Unique Constraint: заголовок и месяц,
    начало и конец недели.
    """

    title = models.CharField(
        max_length=10,
        verbose_name='Заголовок',
        help_text='Укажите название и номер недели.'
    )
    month = models.ForeignKey(
        Month,
        blank=True,
        editable=False,
        on_delete=models.CASCADE,
        verbose_name='Месяц',
        related_name='weeks',
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
        super().clean_fields()
        self.validate_related_obj()
        self.validate_interval()
        self.validate_len_interval()
        return super().clean()

    def clean_fields(self, exclude):
        return None

    def save(self, *args, **kwargs):
        self.month = self.get_related_obj()
        return super().save(*args, **kwargs)


class Schedule(ScheduleMixin, models.Model):
    """
    Модель расписания для пользователей. Содержит семь полей - текст
    расписания, заметки, дату, частоту и количество повторений,
    автора (foreignkey), недели (manytomany):
    1. Поле автор - только для администратора, поле недели - заполняется
    автоматически из значений даты, частоты и количества повторений;
    2. Установлено ограничение на выбор дат: нельзя создать объект расписания
    если нет соответствующего объекта модели Week, нельзя выбрать воскресенье;
    3. Установлен Unique Constraint: автор и дата.
    """

    text = models.TextField(
        max_length=500,
        verbose_name='Расписание пар',
        help_text='Обязательное. Укажите время, название и аудиторию пары.'
    )
    notes = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Заметки',
        help_text='Необязательное. Можно написать заметки для себя.'
    )
    date = models.DateField(
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
        blank=True,
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
        super().clean_fields()
        self.validate_sunday()
        self.validate_empty_repetition()
        self.validate_exist_weeks()
        self.validate_exist_schedule()
        return super().clean()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.week.set(self.get_related_week_objects())
