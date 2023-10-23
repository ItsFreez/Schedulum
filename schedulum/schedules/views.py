from django.views.generic import CreateView, ListView, TemplateView

from schedules.models import Month, Year, Week


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
    pass


class ProfileView(ListView):
    pass
