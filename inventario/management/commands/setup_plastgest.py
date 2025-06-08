# ===================================
# COMMAND: SETUP_PLASTGEST
# Configuración completa del sistema PlastGest
# ===================================

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from inventario.models import Role, UserProfile, Producto
import os

class Command(BaseCommand):
    help = 'Configuración completa del sistema PlastGest'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full-reset',
            action='store_true',
            help='Elimina toda la base de datos y recrea todo desde cero',
        )
        parser.add_argument(
            '--create-admin',
            action='store_true',
            help='Crea un usuario administrador por defecto',
        )
        parser.add_argument(
            '--load-demo',
            action='store_true',
            help='Carga datos de demostración',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                '🚀 CONFIGURANDO PLASTGEST - SISTEMA COMPLETO\n'
                '=' * 50
            )
        )

        try:
            # Paso 1: Migraciones
            self.stdout.write('📦 Paso 1: Aplicando migraciones...')
            call_command('makemigrations', verbosity=0)
            call_command('migrate', verbosity=0)
            self.stdout.write(self.style.SUCCESS('   ✅ Migraciones completadas'))

            # Paso 2: Configurar roles
            self.stdout.write('👥 Paso 2: Configurando roles del sistema...')
            call_command('setup_roles', verbosity=0)
            self.stdout.write(self.style.SUCCESS('   ✅ Roles configurados'))

            # Paso 3: Crear superusuario si se solicita
            if options['create_admin']:
                self.create_admin_user()

            # Paso 4: Cargar datos de demo si se solicita
            if options['load_demo']:
                self.stdout.write('🎭 Paso 4: Cargando datos de demostración...')
                call_command('load_sample_data', '--with-users', verbosity=0)
                self.stdout.write(self.style.SUCCESS('   ✅ Datos de demo cargados'))

            # Paso 5: Verificar configuración
            self.verify_setup()

            # Resumen final
            self.show_final_summary()

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error durante la configuración: {str(e)}')
            )
            return

    def create_admin_user(self):
        """Crea usuario administrador por defecto"""
        self.stdout.write('🔐 Paso 3: Creando usuario administrador...')
        
        try:
            admin_user, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@plastgest.com',
                    'first_name': 'Administrador',
                    'last_name': 'PlastGest',
                    'is_staff': True,
                    'is_superuser': True,
                }
            )
            
            if created:
                admin_user.set_password('admin123456')
                admin_user.save()
                
                # Asignar rol de admin
                try:
                    admin_role = Role.objects.get(name='admin')
                    if hasattr(admin_user, 'profile'):
                        admin_user.profile.role = admin_role
                        admin_user.profile.email_verified = True
                        admin_user.profile.account_active = True
                        admin_user.profile.save()
                except Role.DoesNotExist:
                    pass
                
                self.stdout.write(
                    self.style.SUCCESS(
                        '   ✅ Usuario administrador creado:\n'
                        '      Usuario: admin\n'
                        '      Contraseña: admin123456\n'
                        '      Email: admin@plastgest.com'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING('   ⚠️  Usuario administrador ya existe')
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Error creando administrador: {str(e)}')
            )

    def verify_setup(self):
        """Verifica que todo esté configurado correctamente"""
        self.stdout.write('🔍 Paso 5: Verificando configuración...')
        
        # Verificar roles
        roles_count = Role.objects.count()
        if roles_count >= 5:
            self.stdout.write(f'   ✅ Roles del sistema: {roles_count} configurados')
        else:
            self.stdout.write(f'   ⚠️  Solo {roles_count} roles encontrados')
        
        # Verificar usuarios
        users_count = User.objects.count()
        self.stdout.write(f'   📊 Usuarios en sistema: {users_count}')
        
        # Verificar productos
        products_count = Producto.objects.count()
        if products_count > 0:
            self.stdout.write(f'   📦 Productos en catálogo: {products_count}')
        else:
            self.stdout.write('   📦 Sin productos (usa --load-demo para cargar ejemplos)')
        
        # Verificar perfiles
        profiles_count = UserProfile.objects.count()
        self.stdout.write(f'   👤 Perfiles de usuario: {profiles_count}')

    def show_final_summary(self):
        """Muestra resumen final y próximos pasos"""
        self.stdout.write(
            self.style.SUCCESS(
                '\\n🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!\\n'
                '=' * 50
            )
        )
        
        self.stdout.write('📋 RESUMEN DEL SISTEMA:')
        self.stdout.write(f'   • Roles configurados: {Role.objects.count()}')
        self.stdout.write(f'   • Usuarios registrados: {User.objects.count()}')
        self.stdout.write(f'   • Productos en catálogo: {Producto.objects.count()}')
        self.stdout.write(f'   • Perfiles activos: {UserProfile.objects.count()}')
        
        self.stdout.write('\\n🚀 PRÓXIMOS PASOS:')
        self.stdout.write('   1. Ejecutar: python manage.py runserver')
        self.stdout.write('   2. Ir a: http://127.0.0.1:8000/')
        self.stdout.write('   3. Crear tu cuenta o usar credenciales de demo')
        
        self.stdout.write('\\n🔗 URLS IMPORTANTES:')
        self.stdout.write('   • Aplicación: http://127.0.0.1:8000/')
        self.stdout.write('   • Login: http://127.0.0.1:8000/login/')
        self.stdout.write('   • Registro: http://127.0.0.1:8000/registro/')
        self.stdout.write('   • Admin: http://127.0.0.1:8000/admin/')
        
        # Mostrar credenciales de demo si existen
        if User.objects.filter(email__endswith='@plastgest.com').exists():
            self.stdout.write('\\n👤 USUARIOS DE DEMOSTRACIÓN:')
            demo_users = User.objects.filter(email__endswith='@plastgest.com')
            for user in demo_users:
                role = 'Sin rol'
                if hasattr(user, 'profile') and user.profile.role:
                    role = user.profile.get_role_display()
                self.stdout.write(f'   • {user.username} ({role}) - Contraseña: demo123456')
        
        if User.objects.filter(username='admin').exists():
            self.stdout.write('\\n🔐 ADMINISTRADOR:')
            self.stdout.write('   • Usuario: admin')
            self.stdout.write('   • Contraseña: admin123456')
            self.stdout.write('   • Panel Admin: http://127.0.0.1:8000/admin/')
        
        self.stdout.write('\\n📧 CONFIGURACIÓN DE EMAIL:')
        self.stdout.write('   • Configura tu email real en el archivo .env')
        self.stdout.write('   • Sigue las instrucciones en EMAIL_SETUP.md')
        self.stdout.write('   • El registro requiere verificación por email')
        
        self.stdout.write(
            self.style.SUCCESS(
                '\\n✨ ¡PlastGest está listo para usar!\\n'
                'Gracias por elegir nuestro sistema de gestión.\\n'
            )
        )
