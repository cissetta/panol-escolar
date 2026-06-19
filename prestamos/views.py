# Grupo 3 – Préstamos y Devoluciones
# TODO: implementar las vistas de este módulo
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def index(request):
    """Vista principal del módulo – reemplazar con la implementación real."""
    return render(request, 'prestamos/index.html')
