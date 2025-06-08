# ===================================
# COMMAND: LOAD_SAMPLE_DATA
# Carga datos de prueba para PlastGest
# ===================================

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventario.models import Producto, Role, UserProfile
from inventario.utils import VerificationService, EmailService

class Command(BaseCommand):
    help = 'Carga datos de prueba para PlastGest'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina todos los productos existentes antes de crear nuevos',
        )
        parser.add_argument(
            '--with-users',
            action='store_true',
            help='Crea usuarios de prueba con diferentes roles',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('🗑️ Eliminando productos existentes...')
            Producto.objects.all().delete()

        # Datos de productos plásticos
        productos_data = [
            # Envases
            {
                'nombre': 'Botella PET Transparente 1L',
                'precio': 2.50,
                'stock': 150,
                'categoria': 'Envases',
                'descripcion': 'Botella de PET transparente ideal para bebidas y líquidos. Resistente y reciclable.'
            },
            {
                'nombre': 'Envase Hermético 500ml',
                'precio': 3.25,
                'stock': 80,
                'categoria': 'Envases',
                'descripcion': 'Envase plástico con tapa hermética, perfecto para conservar alimentos.'
            },
            {
                'nombre': 'Bidón Plástico 5L',
                'precio': 12.00,
                'stock': 45,
                'categoria': 'Envases',
                'descripcion': 'Bidón de plástico resistente para almacenamiento de líquidos.'
            },
            {
                'nombre': 'Frasco con Tapa Rosca 250ml',
                'precio': 1.75,
                'stock': 200,
                'categoria': 'Envases',
                'descripcion': 'Frasco plástico con tapa rosca, ideal para conservas y productos caseros.'
            },
            
            # Tuberías
            {
                'nombre': 'Tubería PVC 2 pulgadas x 3m',
                'precio': 15.50,
                'stock': 60,
                'categoria': 'Tuberías',
                'descripcion': 'Tubería de PVC para instalaciones de agua, resistente y duradera.'
            },
            {
                'nombre': 'Codo PVC 90° 2 pulgadas',
                'precio': 4.25,
                'stock': 120,
                'categoria': 'Tuberías',
                'descripcion': 'Codo de PVC de 90 grados para conexiones de tuberías.'
            },
            {
                'nombre': 'Tubería Flexible 1 pulgada x 5m',
                'precio': 22.00,
                'stock': 35,
                'categoria': 'Tuberías',
                'descripcion': 'Tubería flexible para instalaciones que requieren adaptabilidad.'
            },
            
            # Utensilios
            {
                'nombre': 'Cucharas Plásticas (Pack 50)',
                'precio': 8.50,
                'stock': 90,
                'categoria': 'Utensilios',
                'descripcion': 'Pack de 50 cucharas plásticas desechables, ideales para eventos.'
            },
            {
                'nombre': 'Platos Hondos Plásticos (Pack 20)',
                'precio': 15.75,
                'stock': 65,
                'categoria': 'Utensilios',
                'descripcion': 'Platos hondos de plástico resistente, reutilizables y aptos para microondas.'
            },
            {
                'nombre': 'Tazas con Asa (Pack 12)',
                'precio': 18.90,
                'stock': 40,
                'categoria': 'Utensilios',
                'descripcion': 'Tazas plásticas con asa ergonómica, perfectas para bebidas calientes.'
            },
            
            # Bolsas
            {
                'nombre': 'Bolsas Biodegradables 30x40cm (Pack 100)',
                'precio': 12.30,
                'stock': 85,
                'categoria': 'Bolsas',
                'descripcion': 'Bolsas biodegradables ecológicas, resistentes y amigables con el medio ambiente.'
            },
            {
                'nombre': 'Bolsas Transparentes con Cierre 20x25cm (Pack 50)',
                'precio': 7.80,
                'stock': 110,
                'categoria': 'Bolsas',
                'descripcion': 'Bolsas transparentes con cierre hermético, ideales para almacenamiento.'
            },
            
            # Productos Especializados
            {
                'nombre': 'Maceta Plástica con Plato 25cm',
                'precio': 9.75,
                'stock': 70,
                'categoria': 'Jardinería',
                'descripcion': 'Maceta de plástico resistente con plato incluido, perfecta para plantas medianas.'
            },
            {
                'nombre': 'Organizador Multi-compartimentos',
                'precio': 25.50,
                'stock': 30,
                'categoria': 'Organización',
                'descripcion': 'Organizador plástico con múltiples compartimentos para herramientas o materiales.'
            },
            {
                'nombre': 'Bandeja Apilable 40x30cm',
                'precio': 14.20,
                'stock': 55,
                'categoria': 'Organización',
                'descripcion': 'Bandeja plástica apilable, ideal para almacenamiento y organización.'
            },
        ]

        created_count = 0
        for producto_data in productos_data:
            producto, created = Producto.objects.get_or_create(
                nombre=producto_data['nombre'],
                defaults=producto_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'✅ Producto creado: {producto.nombre}')
            else:
                self.stdout.write(f'⚠️  Producto ya existe: {producto.nombre}')

        # Crear usuarios de prueba si se solicita
        if options['with_users']:
            self.create_sample_users()

        # Resumen
        self.stdout.write(
            self.style.SUCCESS(
                f'\\n🎉 Datos de prueba cargados:\\n'
                f'   • {created_count} productos nuevos creados\\n'
                f'   • Total de productos en sistema: {Producto.objects.count()}\\n'
                f'   • Categorías disponibles: {list(Producto.objects.values_list("categoria", flat=True).distinct())}'
            )
        )

    def create_sample_users(self):
        """Crea usuarios de prueba con diferentes roles"""
        users_data = [
            {
                'username': 'gerente_demo',
                'email': 'gerente@plastgest.com',
                'first_name': 'María',
                'last_name': 'González',
                'role': 'gerente',
                'password': 'demo123456'
            },
            {
                'username': 'vendedor_demo',
                'email': 'vendedor@plastgest.com',
                'first_name': 'Carlos',
                'last_name': 'Martínez',
                'role': 'vendedor',
                'password': 'demo123456'
            },
            {
                'username': 'almacenero_demo',
                'email': 'almacen@plastgest.com',
                'first_name': 'Ana',
                'last_name': 'López',
                'role': 'almacenero',
                'password': 'demo123456'
            },
            {
                'username': 'cliente_demo',
                'email': 'cliente@plastgest.com',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'role': 'cliente',
                'password': 'demo123456'
            }
        ]

        for user_data in users_data:
            try:
                user, created = User.objects.get_or_create(
                    username=user_data['username'],
                    defaults={
                        'email': user_data['email'],
                        'first_name': user_data['first_name'],
                        'last_name': user_data['last_name'],
                    }
                )
                
                if created:
                    user.set_password(user_data['password'])
                    user.save()
                    
                    # Asignar rol si existe el perfil
                    if hasattr(user, 'profile'):
                        try:
                            role = Role.objects.get(name=user_data['role'])
                            user.profile.role = role
                            user.profile.email_verified = True  # Para demo
                            user.profile.account_active = True
                            user.profile.save()
                        except Role.DoesNotExist:
                            pass
                    
                    self.stdout.write(f'👤 Usuario demo creado: {user.username} ({user_data["role"]})')
                else:
                    self.stdout.write(f'⚠️  Usuario ya existe: {user.username}')
            
            except Exception as e:
                self.stdout.write(f'❌ Error creando usuario {user_data["username"]}: {str(e)}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\\n👥 Usuarios demo disponibles:\\n'
                f'   • Credenciales: [usuario]@plastgest.com / demo123456\\n'
                f'   • Todos los usuarios tienen email verificado para pruebas'
            )
        )
