from django.apps import AppConfig


class EmployerprofileConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "employerProfile"

    def ready(self):
        import user.signals
