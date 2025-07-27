# plans/apps.py
from django.apps import AppConfig

class PlansConfig(AppConfig):
    name = 'plans'

    def ready(self):
        # importa para que se suscriba a post_migrate
        import plans.signals  # noqa