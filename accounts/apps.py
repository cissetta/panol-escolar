from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Cuentas y Roles'

    def ready(self):
        import accounts.signals  # noqa: F401 – registra señales de Perfil
