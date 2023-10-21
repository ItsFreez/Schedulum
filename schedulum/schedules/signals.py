import datetime as dt

from django.db.models.signals import post_save
from django.dispatch import receiver
from schedules.models import Month, Schedule, Week


@receiver(post_save, sender=Month, dispatch_uid='unique_signal')
def create_weeks(sender, instance, created, **kwargs):
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


@receiver(post_save, sender=Schedule, dispatch_uid='unique_sc_signal')
def add_weeks(sender, instance, created, **kwargs):
    if created:
        print('Началось добавление объекта')
        schedule = Schedule.objects.get(date=instance.date, author=instance.author)
        week_obj = Week.objects.all()
        schedule.week.set(week_obj)
        print('Закончилось добавление объекта')
