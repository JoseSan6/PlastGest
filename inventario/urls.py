from django.urls import path
from . import views

urlpatterns = [
    # URLs principales
    path('productos/', views.lista_productos, name='lista_productos'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),
    
    # URLs de verificación de email
    path('verificar-email/', views.verificar_email_form, name='verificar_email_form'),
    path('verificar-email/<str:token>/', views.verificar_email_token, name='verificar_email_token'),
    path('reenviar-verificacion/', views.reenviar_verificacion, name='reenviar_verificacion'),
    
    # URLs de recuperación de contraseña avanzada
    path('recuperar-contraseña/', views.password_reset_request, name='password_reset_request'),
    path('recuperar-contraseña/enviado/', views.password_reset_done_custom, name='password_reset_done_custom'),
    path('restablecer-contraseña/<str:token>/', views.password_reset_confirm_custom, name='password_reset_confirm_custom'),
    path('recuperar-contraseña/completado/', views.password_reset_complete_custom, name='password_reset_complete_custom'),
    path('recuperar-por-codigo/', views.password_reset_by_code, name='password_reset_by_code'),
    
    # API endpoints
    path('api/verificar-codigo/', views.api_verificar_codigo, name='api_verificar_codigo'),
]


