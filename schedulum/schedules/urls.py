from django.urls import include, path

from schedules.views import (CalendarView, DayListView, IndexView,
                             ProfileView, ScheduleCreate)

app_name = 'schedules'

schedules_urls = [
    path('create/', ScheduleCreate.as_view(), name='create'),
    path('<int:year>/<str:month_title>/<week_title>/',
         DayListView.as_view(),
         name='days')
]

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('schedule/', include(schedules_urls))
]
