from django.urls import include, path

from api.v1.views import get_token, registration

auth_urls = [
    path('signup/', registration, name='registration'),
    path('token/', get_token, name='access_token'),
]

urlpatterns = [
    path('auth/', include(auth_urls)),
]
