from django import forms
from django.contrib.auth.forms import UserCreationForm

from schedules.models import User, Schedule


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации для пользователя."""

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ScheduleCreationForm(forms.ModelForm):
    """Форма для создрания расписания. Автор присваивается автоматически."""

    class Meta:
        model = Schedule
        exclude = ('week',)
        widgets = {
            'author': forms.HiddenInput(),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author')
        return super().__init__(*args, **kwargs)

    def clean_author(self):
        return self.author


class ScheduleEditForm(forms.ModelForm):
    """Форма для редактирования расписания."""

    class Meta:
        model = Schedule
        exclude = ('author', 'date', 'week')
