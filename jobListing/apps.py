from django.apps import AppConfig


class JoblistingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jobListing"

    def ready(self):
        import jobListing.signals
