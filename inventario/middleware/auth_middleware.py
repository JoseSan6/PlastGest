# ===================================
# MIDDLEWARE DE ROLES Y PERMISOS
# PlastGest - Sistema Avanzado de Autenticación
# ===================================

from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

class RolePermissionMiddleware:
    """
    Middleware para manejar roles y permisos en PlastGest
    """
    
    # URLs que requieren autenticación
    PROTECTED_URLS = [
        'lista_productos',
        'admin_panel',
        'inventario_list',
        'pedidos_list',
        'reportes_dashboard',
    ]
    
    # URLs que requieren roles específicos
    ROLE_RESTRICTED_URLS = {
        'admin_panel': ['admin'],
        'inventario_list': ['admin', 'gerente', 'almacenero'],
        'pedidos_list': ['admin', 'gerente', 'vendedor'],
        'reportes_dashboard': ['admin', 'gerente'],
        'user_management': ['admin'],
    }
    
    # URLs públicas (no requieren autenticación)
    PUBLIC_URLS = [
        'login',
        'registro',
        'password_reset_request',
        'password_reset_done_custom',
        'password_reset_confirm_custom',
        'password_reset_complete_custom',
        'verificar_email_form',
        'verificar_email_token',
        'reenviar_verificacion',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Procesa cada vista antes de ejecutarla
        """
        try:
            # Obtener el nombre de la URL actual
            url_name = request.resolver_match.url_name if request.resolver_match else None
            
            if not url_name:
                return None
            
            # Verificar si es una URL pública
            if url_name in self.PUBLIC_URLS:
                return None
            
            # Verificar autenticación para URLs protegidas
            if url_name in self.PROTECTED_URLS and not request.user.is_authenticated:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'authentication_required',
                        'message': 'Debes iniciar sesión para acceder a esta función.',
                        'redirect_url': reverse('login')
                    }, status=401)
                else:
                    messages.warning(request, 'Debes iniciar sesión para acceder a esa página.')
                    return redirect('login')
            
            # Verificar roles para URLs con restricciones específicas
            if (url_name in self.ROLE_RESTRICTED_URLS and 
                request.user.is_authenticated):
                
                required_roles = self.ROLE_RESTRICTED_URLS[url_name]
                user_role = self.get_user_role(request.user)
                
                if user_role not in required_roles:
                    logger.warning(f'Usuario {request.user.username} intentó acceder a {url_name} sin permisos suficientes')
                    
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'error': 'insufficient_permissions',
                            'message': f'No tienes permisos para acceder a esta función. Se requiere rol: {", ".join(required_roles)}.',
                            'required_roles': required_roles,
                            'user_role': user_role
                        }, status=403)
                    else:
                        messages.error(
                            request, 
                            f'No tienes permisos para acceder a esa página. '
                            f'Se requiere uno de estos roles: {", ".join(required_roles)}.'
                        )
                        return redirect('lista_productos')
            
            # Verificar si la cuenta está verificada (solo para URLs protegidas)
            if (url_name in self.PROTECTED_URLS and 
                request.user.is_authenticated and 
                hasattr(request.user, 'profile')):
                
                if not request.user.profile.email_verified:
                    messages.warning(
                        request,
                        'Tu cuenta no ha sido verificada. Revisa tu email para el código de verificación.'
                    )
                    return redirect('verificar_email_form')
                
                if not request.user.profile.account_active:
                    messages.error(
                        request,
                        'Tu cuenta ha sido desactivada. Contacta al administrador.'
                    )
                    return redirect('login')
            
            return None
        
        except Exception as e:
            logger.error(f'Error en RolePermissionMiddleware: {str(e)}')
            return None
    
    def get_user_role(self, user):
        """
        Obtiene el rol del usuario
        """
        try:
            if hasattr(user, 'profile') and user.profile.role:
                return user.profile.role.name
            return 'cliente'  # Rol por defecto
        except Exception as e:
            logger.error(f'Error obteniendo rol de usuario {user.username}: {str(e)}')
            return 'cliente'

class SessionSecurityMiddleware:
    """
    Middleware para seguridad adicional de sesiones
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_request(self, request):
        """
        Procesa la request para verificar seguridad de sesión
        """
        if request.user.is_authenticated:
            try:
                # Verificar si la IP cambió (opcional - puede ser problemático con proxies)
                current_ip = self.get_client_ip(request)
                session_ip = request.session.get('login_ip')
                
                # Actualizar última actividad
                request.session['last_activity'] = request.META.get('REQUEST_TIME_FLOAT')
                
                # Actualizar IP en perfil si es diferente
                if (hasattr(request.user, 'profile') and 
                    request.user.profile.last_login_ip != current_ip):
                    request.user.profile.last_login_ip = current_ip
                    request.user.profile.save(update_fields=['last_login_ip'])
                
            except Exception as e:
                logger.error(f'Error en SessionSecurityMiddleware: {str(e)}')
        
        return None
    
    def get_client_ip(self, request):
        """Obtiene la IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class MessageEnhancementMiddleware:
    """
    Middleware para mejorar el sistema de mensajes
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_template_response(self, request, response):
        """
        Procesa las respuestas de template para agregar contexto adicional
        """
        if hasattr(response, 'context_data') and response.context_data is not None:
            # Agregar información del usuario al contexto
            if request.user.is_authenticated:
                context_data = response.context_data
                context_data['user_role'] = self.get_user_role(request.user)
                context_data['user_permissions'] = self.get_user_permissions(request.user)
                context_data['unread_notifications'] = 3  # Placeholder
        
        return response
    
    def get_user_role(self, user):
        """Obtiene el rol del usuario"""
        try:
            if hasattr(user, 'profile') and user.profile.role:
                return {
                    'name': user.profile.role.name,
                    'display_name': user.profile.role.display_name,
                    'permissions': user.profile.role.permissions
                }
            return {'name': 'cliente', 'display_name': 'Cliente', 'permissions': {}}
        except Exception:
            return {'name': 'cliente', 'display_name': 'Cliente', 'permissions': {}}
    
    def get_user_permissions(self, user):
        """Obtiene los permisos del usuario"""
        try:
            if hasattr(user, 'profile') and user.profile.role:
                return user.profile.role.permissions
            return {}
        except Exception:
            return {}
