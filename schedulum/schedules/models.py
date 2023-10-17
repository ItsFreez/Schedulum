import datetime as dt

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

CURRENT_YEAR = dt.date.today().year
NEXT_YEAR = dt.date.today().year + 1


class Year(models.Model):
    title = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='Заголовок',
        help_text='Это поле автоматически заполнится, оставьте пустым.'
    )
    year = models.SmallIntegerField(
        validators=[MinValueValidator(CURRENT_YEAR),
                    MaxValueValidator(NEXT_YEAR)],
        verbose_name='Год',
        help_text=(
            'Можно указать только текущий и следующий год. Обязательное поле.'
        )
    )

    class Meta:
        verbose_name = 'год'
        verbose_name_plural = 'Годы'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.title = str(self.year) + ' год'
        return super().save(*args, **kwargs)
