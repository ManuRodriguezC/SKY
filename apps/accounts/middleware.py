from django.shortcuts import redirect
from django.urls import resolve

class LoginRequiredMiddleware:
    """
    Redirige al login si el usuario no está autenticado,
    excepto en las rutas que definamos como públicas.
    """

    PUBLIC_VIEWS = {
        "login",
        "logout",
        "verify-account",
        "password_reset",
        "password_reset_done",
        "password_reset_confirm",
        "password_reset_complete",
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):

        if request.user.is_authenticated:
            return self.get_response(request)

        current_view = resolve(request.path_info).url_name

        if current_view in self.PUBLIC_VIEWS:
            return self.get_response(request)

        return redirect("login")