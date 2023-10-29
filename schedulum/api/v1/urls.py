from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.views import ScheduleViewSet, get_token, registration

v1_router = DefaultRouter()
v1_router.register('schedules', ScheduleViewSet, basename='schedule')

auth_urls = [
    path('signup/', registration, name='registration'),
    path('token/', get_token, name='access_token'),
]

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include(auth_urls)),
]
