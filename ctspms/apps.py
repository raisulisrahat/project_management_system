from django.apps import AppConfig


class CtspmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ctspms'

    def ready(self):
        import ctspms.signals
