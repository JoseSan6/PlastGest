from django.apps import AppConfig


class InventarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventario'
    verbose_name = 'Sistema de Inventario PlastGest'
    
    def ready(self):
        # Importar signals para que se registren automáticamente
        import inventario.signals
