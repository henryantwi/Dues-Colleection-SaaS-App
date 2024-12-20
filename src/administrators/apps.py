from django.apps import AppConfig


class AdministratorsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "administrators"

    def ready(self):
        import administrators.signals  # Make sure signals are imported
