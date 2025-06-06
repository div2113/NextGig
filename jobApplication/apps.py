from django.apps import AppConfig


class JobapplicationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jobApplication"

    def ready(self):
        import jobApplication.signals

        # This will ensure that the signals are imported and ready to use when the app is loaded.
        # The signals module contains the logic for handling post_save events for JobApplication.
