from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Producto, Role, UserProfile, VerificationToken

# ===================================
# ADMIN PARA PRODUCTOS
# ===================================
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio', 'stock', 'codigo', 'activo', 'fecha_creacion']
    list_filter = ['categoria', 'activo', 'fecha_creacion']
    search_fields = ['nombre', 'codigo', 'descripcion']
    list_editable = ['precio', 'stock', 'activo']
    readonly_fields = ['codigo', 'fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'categoria', 'descripcion')
        }),
        ('Precios e Inventario', {
            'fields': ('precio', 'stock')
        }),
        ('Configuración', {
            'fields': ('codigo', 'activo')
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

# ===================================
# ADMIN PARA ROLES
# ===================================
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'display_name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Información del Rol', {
            'fields': ('name', 'display_name', 'description')
        }),
        ('Permisos', {
            'fields': ('permissions',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

# ===================================
# ADMIN PARA PERFILES DE USUARIO
# ===================================
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'
    
    fieldsets = (
        ('Rol y Estado', {
            'fields': ('role', 'email_verified', 'phone_verified', 'account_active')
        }),
        ('Información Personal', {
            'fields': ('telefono', 'direccion', 'ciudad', 'pais')
        }),
        ('Metadata', {
            'fields': ('last_login_ip', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

# Extender el UserAdmin para incluir el perfil
class ExtendedUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_role', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'profile__role', 'profile__email_verified']
    
    def get_role(self, obj):
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else 'Sin perfil'
    get_role.short_description = 'Rol'

# Re-registrar User con el admin extendido
admin.site.unregister(User)
admin.site.register(User, ExtendedUserAdmin)

# ===================================
# ADMIN PARA TOKENS DE VERIFICACIÓN
# ===================================
@admin.register(VerificationToken)
class VerificationTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token_type', 'verification_code', 'is_active', 'is_expired_status', 'created_at']
    list_filter = ['token_type', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'verification_code']
    readonly_fields = ['token', 'verification_code', 'created_at', 'used_at']
    
    fieldsets = (
        ('Usuario y Tipo', {
            'fields': ('user', 'token_type')
        }),
        ('Tokens', {
            'fields': ('token', 'verification_code')
        }),
        ('Estado y Tiempo', {
            'fields': ('is_active', 'expires_at', 'attempts')
        }),
        ('Metadata', {
            'fields': ('created_at', 'used_at', 'ip_address'),
            'classes': ('collapse',)
        }),
    )
    
    def is_expired_status(self, obj):
        return '🔴 Expirado' if obj.is_expired else '🟢 Válido'
    is_expired_status.short_description = 'Estado'
    
    actions = ['mark_as_used', 'extend_expiration']
    
    def mark_as_used(self, request, queryset):
        for token in queryset:
            token.mark_as_used()
        self.message_user(request, f'{queryset.count()} tokens marcados como usados.')
    mark_as_used.short_description = 'Marcar como usados'
    
    def extend_expiration(self, request, queryset):
        for token in queryset:
            token.extend_expiration(24)
        self.message_user(request, f'{queryset.count()} tokens extendidos por 24 horas.')
    extend_expiration.short_description = 'Extender expiración (24h)'

# ===================================
# CONFIGURACIÓN DEL ADMIN
# ===================================
admin.site.site_header = 'PlastGest - Administración'
admin.site.site_title = 'PlastGest Admin'
admin.site.index_title = 'Panel de Control - Tienda Virtual de Productos Plásticos'

# Personalizar el admin con colores de la marca
admin.site.site_url = '/productos/'  # Link para "Ver sitio"
