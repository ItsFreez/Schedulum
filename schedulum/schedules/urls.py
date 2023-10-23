from django.urls import path

from schedules.views import IndexView

app_name = 'schedules'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
]
