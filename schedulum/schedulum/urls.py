from django.contrib import admin
from django.views.generic.edit import CreateView
from django.urls import include, path, reverse_lazy

from schedules.forms import CustomUserCreationForm

handler404 = 'schedules.views.page_not_found'
handler500 = 'schedules.views.server_error'

urlpatterns = [
    path('', include('schedules.urls', namespace='schedules')),
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/signup/',
         CreateView.as_view(
             template_name='registration/sign_up.html',
             form_class=CustomUserCreationForm,
             success_url=reverse_lazy('login')
         ),
         name='sign_up')
]
