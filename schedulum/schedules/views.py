import datetime

from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, ListView, TemplateView
from django.urls import reverse_lazy

from schedules.forms import ScheduleCreationForm
from schedules.models import Month, Year, Week, Schedule, User

CURRENT_DAY = datetime.date.today()
NEXT_DAY = CURRENT_DAY + datetime.timedelta(days=1)


class IndexView(TemplateView):
    model = Month
    template_name = 'schedules/index.html'


class CalendarView(ListView):
    model = Month
    template_name = 'schedules/calendar.html'

    def get_queryset(self):
        self.year_objects = Year.objects.all()[:2]
        self.week_objects = Week.objects.all()
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['years'] = self.year_objects
        context['weeks'] = self.week_objects
        return context


class DayListView(ListView):
    pass


class ScheduleCreate(CreateView):
    model = Schedule
    form_class = ScheduleCreationForm
    template_name = 'schedules/create_form.html'
    success_url = reverse_lazy('schedules:calendar')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'author': self.request.user})
        return kwargs


class ProfileView(ListView):
    template_name = 'schedules/profile.html'

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.request.user)
        self.schedules = []
        for day, title in ((CURRENT_DAY, 'Сегодня'), (NEXT_DAY, 'Завтра')):
            week = Week.objects.filter(
                start__lte=day,
                end__gte=day
            ).first()
            schedule = Schedule.objects.filter(
                date__week_day=day.weekday() + 2,
                author=self.user,
                week=week,
            ).first()
            schedule_date_tuple = (schedule, day, title)
            self.schedules.append(schedule_date_tuple)
        return self.schedules

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user
        context['dates'] = [CURRENT_DAY, NEXT_DAY]
        return context
