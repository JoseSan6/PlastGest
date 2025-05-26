# ===================================
# COMMAND: SETUP_ROLES
# Inicializa los roles del sistema para PlastGest
# ===================================

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventario.models import Role, UserProfile

class Command(BaseCommand):
    help = 'Inicializa los roles del sistema PlastGest'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina y recrea todos los roles',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('🗑️ Eliminando roles existentes...')
            Role.objects.all().delete()

        # Definir roles del sistema
        roles_data = [
            {
                'name': 'admin',
                'display_name': '👑 Administrador',
                'description': 'Control total del sistema. Puede gestionar usuarios, configuraciones y todos los módulos.',
                'permissions': {
                    'can_manage_users': True,
                    'can_manage_roles': True,
                    'can_manage_products': True,
                    'can_manage_inventory': True,
                    'can_manage_orders': True,
                    'can_view_reports': True,
                    'can_manage_system': True,
                    'can_delete_anything': True,
                }
            },
            {
                'name': 'gerente',
                'display_name': '📊 Gerente',
                'description': 'Gestión de productos, inventario y reportes. Supervisión de ventas y almacén.',
                'permissions': {
                    'can_manage_products': True,
                    'can_manage_inventory': True,
                    'can_view_orders': True,
                    'can_manage_orders': True,
                    'can_view_reports': True,
                    'can_manage_categories': True,
                    'can_approve_discounts': True,
                }
            },
            {
                'name': 'vendedor',
                'display_name': '🛒 Vendedor',
                'description': 'Atención al cliente, procesamiento de pedidos y consulta de productos.',
                'permissions': {
                    'can_view_products': True,
                    'can_create_orders': True,
                    'can_edit_orders': True,
                    'can_view_customers': True,
                    'can_process_payments': True,
                    'can_apply_discounts': True,
                }
            },
            {
                'name': 'almacenero',
                'display_name': '📦 Almacenero',
                'description': 'Control de stock, recepción de productos y actualización de inventario.',
                'permissions': {
                    'can_view_products': True,
                    'can_update_stock': True,
                    'can_receive_products': True,
                    'can_create_stock_movements': True,
                    'can_view_inventory_reports': True,
                }
            },
            {
                'name': 'cliente',
                'display_name': '👤 Cliente',
                'description': 'Usuario cliente de la tienda virtual. Puede ver productos y realizar pedidos.',
                'permissions': {
                    'can_view_products': True,
                    'can_place_orders': True,
                    'can_view_own_orders': True,
                    'can_edit_profile': True,
                    'can_rate_products': True,
                }
            }
        ]

        created_count = 0
        updated_count = 0

        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={
                    'display_name': role_data['display_name'],
                    'description': role_data['description'],
                    'permissions': role_data['permissions']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Rol creado: {role.display_name}')
                )
            else:
                # Actualizar permisos si el rol ya existe
                role.display_name = role_data['display_name']
                role.description = role_data['description']
                role.permissions = role_data['permissions']
                role.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'🔄 Rol actualizado: {role.display_name}')
                )

        # Resumen
        self.stdout.write(
            self.style.SUCCESS(
                f'\\n🎉 Proceso completado:\\n'
                f'   • {created_count} roles creados\\n'
                f'   • {updated_count} roles actualizados\\n'
                f'   • Total de roles en sistema: {Role.objects.count()}'
            )
        )

        # Mostrar usuarios sin rol asignado
        users_without_role = User.objects.filter(profile__role__isnull=True)
        if users_without_role.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'\\n⚠️  Usuarios sin rol asignado: {users_without_role.count()}'
                )
            )
            for user in users_without_role:
                self.stdout.write(f'   • {user.username} ({user.email})')
            
            self.stdout.write('\\n💡 Tip: Asigna roles manualmente desde el admin o crea un superusuario.')
