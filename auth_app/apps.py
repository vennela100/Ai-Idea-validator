from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.contrib.auth'
    name = 'auth_app'
    verbose_name = 'Authentication'
