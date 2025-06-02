# ===================================
# COMANDO PARA CONFIGURAR ROLES DEL SISTEMA
# PlastGest - Setup de Roles y Permisos
# ===================================

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventario.models import Role, UserProfile

class Command(BaseCommand):
    help = 'Configura los roles por defecto del sistema PlastGest'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create-admin',
            action='store_true',
            help='Crear usuario administrador por defecto',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🎯 Configurando roles del sistema PlastGest...')
        )
        
        # Definir roles con sus permisos
        roles_data = [
            {
                'name': 'admin',
                'display_name': '👑 Administrador',
                'description': 'Acceso completo al sistema',
                'permissions': {
                    'can_view_products': True,
                    'can_add_products': True,
                    'can_edit_products': True,
                    'can_delete_products': True,
                    'can_manage_inventory': True,
                    'can_view_all_orders': True,
                    'can_manage_orders': True,
                    'can_view_reports': True,
                    'can_manage_users': True,
                    'can_manage_roles': True,
                    'can_access_admin': True,
                    'can_configure_system': True,
                }
            },
            {
                'name': 'gerente',
                'display_name': '📊 Gerente',
                'description': 'Gestión operativa y reportes',
                'permissions': {
                    'can_view_products': True,
                    'can_add_products': True,
                    'can_edit_products': True,
                    'can_manage_inventory': True,
                    'can_view_all_orders': True,
                    'can_manage_orders': True,
                    'can_view_reports': True,
                    'can_manage_users': False,
                    'can_access_admin': False,
                }
            },
            {
                'name': 'vendedor',
                'display_name': '🛒 Vendedor',
                'description': 'Gestión de ventas y pedidos',
                'permissions': {
                    'can_view_products': True,
                    'can_add_products': False,
                    'can_edit_products': False,
                    'can_view_inventory': True,
                    'can_view_all_orders': True,
                    'can_manage_orders': True,
                    'can_create_orders': True,
                    'can_view_reports': False,
                }
            },
            {
                'name': 'almacenero',
                'display_name': '📦 Almacenero',
                'description': 'Gestión de inventario y almacén',
                'permissions': {
                    'can_view_products': True,
                    'can_add_products': True,
                    'can_edit_products': True,
                    'can_manage_inventory': True,
                    'can_view_orders': True,
                    'can_update_order_status': True,
                    'can_view_reports': False,
                }
            },
            {
                'name': 'cliente',
                'display_name': '👤 Cliente',
                'description': 'Usuario cliente de la tienda virtual',
                'permissions': {
                    'can_view_products': True,
                    'can_place_orders': True,
                    'can_view_own_orders': True,
                    'can_edit_profile': True,
                    'can_track_orders': True,
                }
            },
        ]
        
        # Crear o actualizar roles
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
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Rol creado: {role.display_name}')
                )
            else:
                # Actualizar permisos si el rol ya existe
                role.display_name = role_data['display_name']
                role.description = role_data['description']
                role.permissions = role_data['permissions']
                role.save()
                self.stdout.write(
                    self.style.WARNING(f'🔄 Rol actualizado: {role.display_name}')
                )
        
        # Crear usuario administrador si se solicita
        if options['create_admin']:
            self.create_admin_user()
        
        # Estadísticas finales
        total_roles = Role.objects.count()
        total_users = User.objects.count()
        total_profiles = UserProfile.objects.count()
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('📊 ESTADÍSTICAS DEL SISTEMA:'))
        self.stdout.write(f'   • Roles configurados: {total_roles}')
        self.stdout.write(f'   • Usuarios registrados: {total_users}')
        self.stdout.write(f'   • Perfiles creados: {total_profiles}')
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS('🎉 ¡Roles configurados exitosamente!')
        )
    
    def create_admin_user(self):
        """Crea un usuario administrador por defecto"""
        try:
            # Verificar si ya existe un admin
            admin_role = Role.objects.get(name='admin')
            existing_admin = UserProfile.objects.filter(role=admin_role).first()
            
            if existing_admin:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  Ya existe un administrador: {existing_admin.user.username}'
                    )
                )
                return
            
            # Crear usuario admin
            username = 'admin'
            email = 'admin@plastgest.com'
            password = 'admin123456'  # Cambiar en producción
            
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Usuario {username} ya existe')
                )
                return
            
            # Crear usuario
            admin_user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='Administrador',
                last_name='PlastGest',
                is_staff=True,
                is_superuser=True
            )
            
            # Crear perfil con rol admin
            profile = UserProfile.objects.create(
                user=admin_user,
                role=admin_role,
                email_verified=True,
                account_active=True
            )
            
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('👑 USUARIO ADMINISTRADOR CREADO:'))
            self.stdout.write(f'   • Usuario: {username}')
            self.stdout.write(f'   • Email: {email}')
            self.stdout.write(f'   • Contraseña: {password}')
            self.stdout.write(f'   • Rol: {admin_role.display_name}')
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  IMPORTANTE: Cambia la contraseña del administrador en producción'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creando administrador: {str(e)}')
            )
