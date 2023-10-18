from django.apps import AppConfig


class SchedulesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'schedules'

    def ready(self) -> None:
        import schedules.signals
        return super().ready()
