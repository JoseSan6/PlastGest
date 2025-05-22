from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm
from django.contrib.auth import login as auth_login

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
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
    # Aquí puedes agregar lógica para obtener productos de la base de datos
    return render(request, 'inventario/lista_productos.html')
def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Loguear automáticamente al usuario
            return redirect('lista_productos')
    else:
        form = RegistroForm()
    return render(request, 'inventario/registro.html', {'form': form})
