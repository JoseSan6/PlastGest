# ===================================
# CONFIGURACIÓN DE EMAIL PARA PLASTGEST
# Instrucciones paso a paso
# ===================================

## 🚀 CONFIGURACIÓN RÁPIDA CON GMAIL

### Paso 1: Preparar tu cuenta de Gmail
1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. Ve a **Seguridad** > **Verificación en 2 pasos**
3. **Activa** la verificación en 2 pasos si no la tienes

### Paso 2: Crear contraseña de aplicación
1. En **Seguridad**, busca **Contraseñas de aplicaciones**
2. Selecciona **Mail** y **Windows Computer**
3. Google te dará una contraseña de 16 caracteres como: `abcd efgh ijkl mnop`

### Paso 3: Configurar tu archivo .env
Abre el archivo `.env` y reemplaza estas líneas:

```env
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
DEFAULT_FROM_EMAIL=PlastGest <tu_email@gmail.com>
```

**Ejemplo real:**
```env
EMAIL_HOST_USER=juan.perez@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
DEFAULT_FROM_EMAIL=PlastGest <juan.perez@gmail.com>
```

### Paso 4: Probar la configuración
```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
send_mail(
    'Prueba PlastGest',
    'Email configurado correctamente!',
    'tu_email@gmail.com',
    ['tu_email@gmail.com'],
    fail_silently=False,
)
```

---

## 🔧 OTRAS OPCIONES DE EMAIL

### Para Outlook/Hotmail:
```env
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu_email@outlook.com
EMAIL_HOST_PASSWORD=tu_contraseña
```

### Para Yahoo:
```env
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu_email@yahoo.com
EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion
```

---

## 🚨 SOLUCIÓN DE PROBLEMAS

### Error: "SMTPAuthenticationError"
- ✅ Verifica que la verificación en 2 pasos esté activa
- ✅ Usa la contraseña de aplicación, NO tu contraseña normal
- ✅ Verifica que el email sea correcto

### Error: "SMTPConnectTimeoutError"
- ✅ Verifica tu conexión a Internet
- ✅ Algunos ISP bloquean el puerto 587, usa el 465 con SSL

### Para usar puerto 465 (SSL):
```env
EMAIL_PORT=465
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
```

---

## ✅ VERIFICAR QUE FUNCIONA

Después de configurar, ejecuta:

```bash
python manage.py runserver
```

1. Regístrate con tu email real
2. Deberías recibir un email de verificación
3. Si no llega, revisa tu carpeta de SPAM

---

## 🎯 CONFIGURACIÓN PARA PRODUCCIÓN

Para producción, considera usar:
- **SendGrid**: Servicio profesional de emails
- **Amazon SES**: Servicio de AWS
- **Mailgun**: Alternativa robusta

Ejemplo con SendGrid:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=tu_api_key_de_sendgrid
```
