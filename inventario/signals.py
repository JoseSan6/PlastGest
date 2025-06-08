# ===================================
# SIGNALS PARA PLASTGEST
# Automatización de creación de perfiles y roles
# ===================================

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Role, VerificationToken

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automáticamente crea un perfil de usuario cuando se registra un nuevo usuario
    """
    if created:
        # Obtener o crear rol por defecto para nuevos usuarios
        default_role, _ = Role.objects.get_or_create(
            name='cliente',
            defaults={
                'display_name': '👤 Cliente',
                'description': 'Usuario cliente de la tienda virtual',
                'permissions': {
                    'can_view_products': True,
                    'can_place_orders': True,
                    'can_view_own_orders': True,
                    'can_edit_profile': True,
                }
            }
        )
        
        # Crear perfil del usuario
        UserProfile.objects.create(
            user=instance,
            role=default_role,
            email_verified=False,  # Requerirá verificación
            account_active=False   # Activará después de verificar email
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Guarda el perfil del usuario cuando se actualiza el usuario
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()

# Signal para crear token de verificación automáticamente
@receiver(post_save, sender=User)
def create_verification_token(sender, instance, created, **kwargs):
    """
    Crea automáticamente un token de verificación de email para nuevos usuarios
    """
    if created and instance.email:
        VerificationToken.objects.create(
            user=instance,
            token_type='email_verification'
        )
