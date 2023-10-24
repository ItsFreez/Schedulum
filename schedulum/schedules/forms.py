from django import forms
from django.contrib.auth.forms import UserCreationForm

from schedules.models import User, Schedule


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ScheduleCreationForm(forms.ModelForm):

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
