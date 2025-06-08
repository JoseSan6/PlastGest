# ===================================
# UTILIDADES PARA SISTEMA DE AUTENTICACIÓN
# PlastGest - Tienda Virtual de Productos Plásticos
# ===================================

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User
from .models import VerificationToken
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Servicio centralizado para el envío de emails"""
    
    @staticmethod
    def send_verification_email(user, verification_token):
        """
        Envía email de verificación de cuenta
        """
        try:
            subject = f'{settings.EMAIL_SUBJECT_PREFIX}Verifica tu cuenta en PlastGest'
            
            # Contexto para el template
            context = {
                'user': user,
                'token': verification_token,
                'site_name': 'PlastGest',
                'site_url': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
                'verification_url': f"{getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')}/verificar-email/{verification_token.token}/",
                'verification_code': verification_token.verification_code,
                'expires_hours': 24,
            }
            
            # Renderizar templates
            html_message = render_to_string('emails/verification_email.html', context)
            plain_message = render_to_string('emails/verification_email.txt', context)
            
            # Enviar email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f'Email de verificación enviado a {user.email}')
            return True
        
        except Exception as e:
            logger.error(f'Error enviando email de verificación a {user.email}: {str(e)}')
            return False
    
    @staticmethod
    def send_password_reset_email(user, verification_token):
        """
        Envía email de recuperación de contraseña
        """
        try:
            subject = f'{settings.EMAIL_SUBJECT_PREFIX}Recupera tu contraseña'
            
            context = {
                'user': user,
                'token': verification_token,
                'site_name': 'PlastGest',
                'site_url': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
                'reset_url': f"{getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')}/restablecer-contraseña/{verification_token.token}/",
                'verification_code': verification_token.verification_code,
                'expires_hours': 2,  # Las contraseñas expiran más rápido
            }
            
            html_message = render_to_string('emails/password_reset_email.html', context)
            plain_message = render_to_string('emails/password_reset_email.txt', context)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f'Email de recuperación enviado a {user.email}')
            return True
        
        except Exception as e:
            logger.error(f'Error enviando email de recuperación a {user.email}: {str(e)}')
            return False
    
    @staticmethod
    def send_welcome_email(user):
        """
        Envía email de bienvenida después de verificar la cuenta
        """
        try:
            subject = f'{settings.EMAIL_SUBJECT_PREFIX}¡Bienvenido a PlastGest!'
            
            context = {
                'user': user,
                'site_name': 'PlastGest',
                'site_url': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
                'login_url': f"{getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')}/login/",
                'products_url': f"{getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')}/productos/",
            }
            
            html_message = render_to_string('emails/welcome_email.html', context)
            plain_message = render_to_string('emails/welcome_email.txt', context)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f'Email de bienvenida enviado a {user.email}')
            return True
        
        except Exception as e:
            logger.error(f'Error enviando email de bienvenida a {user.email}: {str(e)}')
            return False

class VerificationService:
    """Servicio para manejar verificaciones de usuario"""
    
    @staticmethod
    def create_verification_token(user, token_type='email_verification', expires_hours=24):
        """Crea un nuevo token de verificación"""
        from datetime import timedelta
        from django.utils import timezone
        
        # Desactivar tokens anteriores del mismo tipo
        VerificationToken.objects.filter(
            user=user, 
            token_type=token_type, 
            is_active=True
        ).update(is_active=False)
        
        # Crear nuevo token
        token = VerificationToken.objects.create(
            user=user,
            token_type=token_type,
            expires_at=timezone.now() + timedelta(hours=expires_hours)
        )
        
        return token
    
    @staticmethod
    def verify_email_token(token_string):
        """Verifica un token de email"""
        try:
            token = VerificationToken.objects.get(
                token=token_string,
                token_type='email_verification',
                is_active=True
            )
            
            if not token.is_valid:
                return False, "Token expirado o inválido"
            
            # Marcar email como verificado
            user = token.user
            if hasattr(user, 'profile'):
                user.profile.email_verified = True
                user.profile.account_active = True
                user.profile.save()
            
            # Marcar token como usado
            token.mark_as_used()
            
            # Enviar email de bienvenida
            EmailService.send_welcome_email(user)
            
            return True, f"Email verificado correctamente para {user.username}"
        
        except VerificationToken.DoesNotExist:
            return False, "Token no encontrado"
        except Exception as e:
            logger.error(f'Error verificando token: {str(e)}')
            return False, "Error interno del servidor"
    
    @staticmethod
    def verify_by_code(user, code, token_type='email_verification'):
        """Verifica usando código de 6 dígitos"""
        try:
            token = VerificationToken.objects.get(
                user=user,
                verification_code=code,
                token_type=token_type,
                is_active=True
            )
            
            if not token.is_valid:
                return False, "Código expirado o inválido"
            
            # Marcar como verificado
            if token_type == 'email_verification' and hasattr(user, 'profile'):
                user.profile.email_verified = True
                user.profile.account_active = True
                user.profile.save()
            
            token.mark_as_used()
            
            if token_type == 'email_verification':
                EmailService.send_welcome_email(user)
            
            return True, "Verificación exitosa"
        
        except VerificationToken.DoesNotExist:
            return False, "Código incorrecto"
        except Exception as e:
            logger.error(f'Error verificando código: {str(e)}')
            return False, "Error interno del servidor"

def get_client_ip(request):
    """Obtiene la IP real del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
