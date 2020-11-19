from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'muni_portal.core'

    def ready(self):
        import muni_portal.core.signals
