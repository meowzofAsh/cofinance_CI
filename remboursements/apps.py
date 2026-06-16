from django.apps import AppConfig


class RemboursementsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "remboursements"

    def ready(self):
        import remboursements.signals
