# from .celery_conf import celery_app
# src/__init__.py

# __all__ = ['celery_app']


# src/__init__.py

from .celery import app as celery_app

__all__ = ['celery_app']
