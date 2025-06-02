from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from .forms import RegistroForm
from .models import Producto, VerificationToken
from .utils import EmailService, VerificationService, get_client_ip
import logging

logger = logging.getLogger(__name__)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Verificar si la cuenta está verificada y activa
            if hasattr(user, 'profile'):
                if not user.profile.email_verified:
                    messages.warning(
                        request, 
                        'Tu cuenta no ha sido verificada. Revisa tu email para el código de verificación. '
                        '<a href="{}">¿No recibiste el email?</a>'.format(
                            reverse('reenviar_verificacion') + f'?email={user.email}'
                        )
                    )
                    return render(request, 'inventario/login.html')
                
                if not user.profile.account_active:
                    messages.error(request, 'Tu cuenta ha sido desactivada. Contacta al administrador.')
                    return render(request, 'inventario/login.html')
            
            # Registrar IP de login
            if hasattr(user, 'profile'):
                user.profile.last_login_ip = get_client_ip(request)
                user.profile.save()
            
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.first_name or user.username}!')
            return redirect('lista_productos')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'inventario/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'inventario/lista_productos.html', {'productos': productos})

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            # Crear usuario pero no hacer login automático
            user = form.save()
            
            try:
                # Crear token de verificación
                verification_token = VerificationService.create_verification_token(
                    user, 'email_verification', expires_hours=24
                )
                
                # Enviar email de verificación
                email_sent = EmailService.send_verification_email(user, verification_token)
                
                if email_sent:
                    messages.success(
                        request, 
                        f'¡Cuenta creada exitosamente! Se ha enviado un código de verificación a {user.email}. '
                        'Revisa tu bandeja de entrada y spam.'
                    )
                    # Redirigir a página de verificación
                    return redirect('verificar_email_form')
                else:
                    messages.warning(
                        request,
                        'Cuenta creada pero hubo un problema enviando el email de verificación. '
                        'Intenta reenviar el código de verificación.'
                    )
                    return redirect('reenviar_verificacion')
            
            except Exception as e:
                logger.error(f'Error en registro: {str(e)}')
                messages.error(
                    request,
                    'Hubo un problema al crear tu cuenta. Por favor, intenta de nuevo.'
                )
        else:
            # Mostrar errores del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegistroForm()
    
    return render(request, 'inventario/registro.html', {'form': form})

# ===================================
# VISTAS DE VERIFICACIÓN DE EMAIL
# ===================================

def verificar_email_form(request):
    """
    Formulario para ingresar código de verificación
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        codigo = request.POST.get('codigo')
        
        if not email or not codigo:
            messages.error(request, 'Email y código son requeridos.')
            return render(request, 'inventario/verificar_email.html')
        
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(email=email)
            
            # Verificar código
            success, message = VerificationService.verify_by_code(
                user, codigo, 'email_verification'
            )
            
            if success:
                messages.success(request, message + ' Ya puedes iniciar sesión.')
                return redirect('login')
            else:
                messages.error(request, message)
        
        except User.DoesNotExist:
            messages.error(request, 'No se encontró un usuario con ese email.')
        except Exception as e:
            logger.error(f'Error verificando código: {str(e)}')
            messages.error(request, 'Error interno. Inténtalo de nuevo.')
    
    return render(request, 'inventario/verificar_email.html')

def verificar_email_token(request, token):
    """
    Verificación por link/token directo
    """
    success, message = VerificationService.verify_email_token(token)
    
    if success:
        messages.success(request, 'Email verificado correctamente. ¡Ya puedes iniciar sesión!')
        return redirect('login')
    else:
        messages.error(request, f'Error en la verificación: {message}')
        return redirect('verificar_email_form')

def reenviar_verificacion(request):
    """
    Reenvío de código de verificación
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if not email:
            messages.error(request, 'El email es requerido.')
            return render(request, 'inventario/reenviar_verificacion.html')
        
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(email=email)
            
            # Verificar si ya está verificado
            if hasattr(user, 'profile') and user.profile.email_verified:
                messages.info(request, 'Esta cuenta ya está verificada. Puedes iniciar sesión.')
                return redirect('login')
            
            # Crear nuevo token
            verification_token = VerificationService.create_verification_token(
                user, 'email_verification', expires_hours=24
            )
            
            # Enviar email
            email_sent = EmailService.send_verification_email(user, verification_token)
            
            if email_sent:
                messages.success(
                    request,
                    f'Se ha reenviado el código de verificación a {email}. '
                    'Revisa tu bandeja de entrada y spam.'
                )
                return redirect('verificar_email_form')
            else:
                messages.error(request, 'Error enviando el email. Intenta más tarde.')
        
        except User.DoesNotExist:
            messages.error(request, 'No se encontró un usuario con ese email.')
        except Exception as e:
            logger.error(f'Error reenviando verificación: {str(e)}')
            messages.error(request, 'Error interno. Inténtalo de nuevo.')
    
    # Prellenar email si viene en GET
    email = request.GET.get('email', '')
    return render(request, 'inventario/reenviar_verificacion.html', {'email': email})

# ===================================
# SISTEMA DE RECUPERACIÓN DE CONTRASEÑA AVANZADO
# ===================================

def password_reset_request(request):
    """
    Solicitud de restablecimiento de contraseña personalizada
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if not email:
            messages.error(request, 'El email es requerido.')
            return render(request, 'inventario/password_reset_request.html')
        
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(email=email)
            
            # Crear token de recuperación (expira en 2 horas)
            reset_token = VerificationService.create_verification_token(
                user, 'password_reset', expires_hours=2
            )
            
            # Enviar email de recuperación
            email_sent = EmailService.send_password_reset_email(user, reset_token)
            
            if email_sent:
                messages.success(
                    request,
                    f'Se ha enviado un enlace de recuperación a {email}. '
                    'Revisa tu bandeja de entrada y spam. El enlace expira en 2 horas.'
                )
                return redirect('password_reset_done_custom')
            else:
                messages.error(request, 'Error enviando el email. Intenta más tarde.')
        
        except User.DoesNotExist:
            # Por seguridad, no revelamos si el email existe o no
            messages.success(
                request,
                'Si el email existe en nuestro sistema, recibirás un enlace de recuperación.'
            )
            return redirect('password_reset_done_custom')
        except Exception as e:
            logger.error(f'Error en recuperación de contraseña: {str(e)}')
            messages.error(request, 'Error interno. Inténtalo de nuevo.')
    
    return render(request, 'inventario/password_reset_request.html')

def password_reset_done_custom(request):
    """
    Página de confirmación de envío de email
    """
    return render(request, 'inventario/password_reset_done.html')

def password_reset_confirm_custom(request, token):
    """
    Confirmación y cambio de contraseña con token personalizado
    """
    try:
        # Verificar token
        reset_token = VerificationToken.objects.get(
            token=token,
            token_type='password_reset',
            is_active=True
        )
        
        if not reset_token.is_valid:
            messages.error(
                request, 
                'El enlace de recuperación ha expirado o es inválido. '
                'Solicita un nuevo enlace de recuperación.'
            )
            return redirect('password_reset_request')
        
        user = reset_token.user
        
        if request.method == 'POST':
            password1 = request.POST.get('new_password1')
            password2 = request.POST.get('new_password2')
            
            if not password1 or not password2:
                messages.error(request, 'Ambos campos de contraseña son requeridos.')
            elif password1 != password2:
                messages.error(request, 'Las contraseñas no coinciden.')
            elif len(password1) < 8:
                messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            else:
                try:
                    # Validar contraseña con validadores de Django
                    from django.contrib.auth.password_validation import validate_password
                    validate_password(password1, user)
                    
                    # Cambiar contraseña
                    user.set_password(password1)
                    user.save()
                    
                    # Marcar token como usado
                    reset_token.mark_as_used()
                    
                    # Registrar IP
                    if hasattr(user, 'profile'):
                        user.profile.last_login_ip = get_client_ip(request)
                        user.profile.save()
                    
                    messages.success(
                        request,
                        '¡Contraseña cambiada exitosamente! Ya puedes iniciar sesión con tu nueva contraseña.'
                    )
                    return redirect('password_reset_complete_custom')
                
                except Exception as validation_error:
                    messages.error(request, f'Error de validación: {str(validation_error)}')
        
        return render(request, 'inventario/password_reset_confirm.html', {
            'token': token,
            'user': user,
            'expires_at': reset_token.expires_at
        })
    
    except VerificationToken.DoesNotExist:
        messages.error(
            request,
            'Enlace de recuperación inválido. Solicita un nuevo enlace.'
        )
        return redirect('password_reset_request')
    except Exception as e:
        logger.error(f'Error en confirmación de reset: {str(e)}')
        messages.error(request, 'Error interno. Inténtalo de nuevo.')
        return redirect('password_reset_request')

def password_reset_complete_custom(request):
    """
    Página de confirmación de cambio exitoso
    """
    return render(request, 'inventario/password_reset_complete.html')

def password_reset_by_code(request):
    """
    Recuperación usando código de 6 dígitos
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        codigo = request.POST.get('codigo')
        new_password = request.POST.get('new_password')
        
        if not all([email, codigo, new_password]):
            messages.error(request, 'Todos los campos son requeridos.')
            return render(request, 'inventario/password_reset_by_code.html')
        
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(email=email)
            
            # Verificar código
            success, message = VerificationService.verify_by_code(
                user, codigo, 'password_reset'
            )
            
            if success:
                # Cambiar contraseña
                user.set_password(new_password)
                user.save()
                
                messages.success(
                    request,
                    'Contraseña cambiada exitosamente. Ya puedes iniciar sesión.'
                )
                return redirect('login')
            else:
                messages.error(request, message)
        
        except User.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
        except Exception as e:
            logger.error(f'Error en reset por código: {str(e)}')
            messages.error(request, 'Error interno. Inténtalo de nuevo.')
    
    return render(request, 'inventario/password_reset_by_code.html')

# ===================================
# API ENDPOINTS (JSON)
# ===================================

@require_http_methods(["POST"])
def api_verificar_codigo(request):
    """
    API endpoint para verificar código (AJAX)
    """
    try:
        import json
        data = json.loads(request.body)
        email = data.get('email')
        codigo = data.get('codigo')
        
        if not email or not codigo:
            return JsonResponse({
                'success': False,
                'message': 'Email y código son requeridos.'
            })
        
        from django.contrib.auth.models import User
        user = User.objects.get(email=email)
        
        success, message = VerificationService.verify_by_code(
            user, codigo, 'email_verification'
        )
        
        return JsonResponse({
            'success': success,
            'message': message,
            'redirect_url': reverse('login') if success else None
        })
    
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Usuario no encontrado.'
        })
    except Exception as e:
        logger.error(f'Error en API verificación: {str(e)}')
        return JsonResponse({
            'success': False,
            'message': 'Error interno del servidor.'
        })
