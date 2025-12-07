from django.apps import AppConfig


class SchedulerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scheduler'

    # Start the scheduler on startup
    def ready(self):
        from .jobs import start_scheduler
        start_scheduler()