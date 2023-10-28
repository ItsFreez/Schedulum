import datetime as dt

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from schedules.models import Month, Week, Schedule


@receiver(post_save, sender=Month, dispatch_uid='unique_signal')
def create_weeks(sender, instance, created, **kwargs):
    """Сигнал для автоматического создания объектов Week при создании Month."""
    if created:
        difference = instance.end - instance.start
        count_weeks = (difference.days + 1) // 7
        all_weeks = []
        for num_week in range(count_weeks):
            title_week = 'Неделя ' + str(num_week + 1)
            start_count = num_week * 7
            end_count = start_count + 6
            start_week = instance.start + dt.timedelta(days=start_count)
            end_week = instance.start + dt.timedelta(days=end_count)
            week = Week(title=title_week,
                        month=Month.objects.get(id=instance.id),
                        start=start_week, end=end_week)
            all_weeks.append(week)
        Week.objects.bulk_create(all_weeks)


@receiver(pre_delete, sender=Week, dispatch_uid='unique_signal')
def delete_related_schedules(sender, instance, **kwargs):
    """Сигнал для удаления всех объектов Schedule, связанных с Week."""
    Schedule.objects.filter(week=instance).delete()
