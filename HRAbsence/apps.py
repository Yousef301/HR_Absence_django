from django.apps import AppConfig


class HrabsenceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "HRAbsence"

    def ready(self):
        import HRAbsence.signals
