"""
Decoradores para restringir vistas por rol.

Uso:
    from accounts.decorators import rol_requerido

    @login_required
    @rol_requerido('ADMIN', 'PANOLERO')
    def mi_vista(request):
        ...
"""
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from functools import wraps


def rol_requerido(*roles):
    """
    Restringe una vista a los roles indicados.
    Lanza PermissionDenied (403) si el usuario no tiene el rol correcto.
    """
    def decorador(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            try:
                perfil = request.user.perfil
            except Exception:
                raise PermissionDenied
            if perfil.rol not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorador


# Atajos listos para usar
solo_admin    = rol_requerido('ADMIN')
solo_panolero = rol_requerido('ADMIN', 'PANOLERO')
solo_docente  = rol_requerido('ADMIN', 'PANOLERO', 'DOCENTE')
