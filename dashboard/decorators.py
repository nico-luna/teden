from functools import wraps
from django.shortcuts import redirect


def seller_required(view_func):
    """Decorator que asegura que el usuario sea seller y tenga sellerprofile.

    Si no es seller o no tiene sellerprofile, redirige a la vista
    `convertirse_en_vendedor`.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = getattr(request, 'user', None)
        if not user or not getattr(user, 'is_authenticated', False):
            # Dejar que el decorador @login_required redirija al login cuando
            # corresponda; aquí hacemos una redirección por seguridad.
            return redirect('login')

        if getattr(user, 'role', None) != 'seller' or not hasattr(user, 'sellerprofile'):
            return redirect('convertirse_en_vendedor')

        return view_func(request, *args, **kwargs)

    return _wrapped_view
