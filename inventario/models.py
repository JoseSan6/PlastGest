from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import secrets
import string

# ===================================
# MODELO DE PRODUCTO (Original)
# ===================================
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    categoria = models.CharField(max_length=50, blank=True, help_text="Ej: Envases, Tuberías, Utensilios")
    descripcion = models.TextField(blank=True)
    codigo = models.CharField(max_length=20, unique=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} - Stock: {self.stock}"

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self.generar_codigo()
        super().save(*args, **kwargs)

    def generar_codigo(self):
        return f"PLAST-{secrets.token_hex(4).upper()}"

# ===================================
# SISTEMA DE ROLES PARA TIENDA VIRTUAL
# ===================================
class Role(models.Model):
    ROLE_CHOICES = [
        ('admin', '👑 Administrador'),
        ('gerente', '📊 Gerente'),
        ('vendedor', '🛒 Vendedor'),
        ('almacenero', '📦 Almacenero'),
        ('cliente', '👤 Cliente'),
    ]
    
    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)
    display_name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    permissions = models.JSONField(default=dict, help_text="Permisos específicos del rol")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
    
    def __str__(self):
        return self.get_name_display()

# ===================================
# PERFIL EXTENDIDO DE USUARIO
# ===================================
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Información Personal
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.TextField(blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    pais = models.CharField(max_length=100, default='Perú')
    
    # Estado de la cuenta
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    account_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
    
    def get_role_display(self):
        return self.role.display_name if self.role else "Sin rol asignado"
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username

# ===================================
# TOKENS DE VERIFICACIÓN
# ===================================
class VerificationToken(models.Model):
    TOKEN_TYPES = [
        ('email_verification', 'Verificación de Email'),
        ('password_reset', 'Recuperación de Contraseña'),
        ('phone_verification', 'Verificación de Teléfono'),
        ('account_activation', 'Activación de Cuenta'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.CharField(max_length=100, unique=True)
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPES)
    
    # Token de 6 dígitos para códigos de verificación
    verification_code = models.CharField(max_length=6, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Estado
    is_active = models.BooleanField(default=True)
    attempts = models.IntegerField(default=0)  # Intentos de uso
    
    class Meta:
        verbose_name = "Token de Verificación"
        verbose_name_plural = "Tokens de Verificación"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_token_type_display()}"
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_secure_token()
        if not self.verification_code:
            self.verification_code = self.generate_verification_code()
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)  # 24 horas por defecto
        super().save(*args, **kwargs)
    
    def generate_secure_token(self):
        """Genera un token seguro de 64 caracteres"""
        return secrets.token_urlsafe(48)
    
    def generate_verification_code(self):
        """Genera un código de verificación de 6 dígitos"""
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    @property
    def is_expired(self):
        """Verifica si el token ha expirado"""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Verifica si el token es válido (activo, no usado, no expirado)"""
        return self.is_active and not self.used_at and not self.is_expired
    
    def mark_as_used(self):
        """Marca el token como usado"""
        self.used_at = timezone.now()
        self.is_active = False
        self.save()
    
    def extend_expiration(self, hours=24):
        """Extiende la expiración del token"""
        self.expires_at = timezone.now() + timedelta(hours=hours)
        self.save()