from collections import defaultdict

from django.contrib.auth.models import Permission


TRANSLATIONS = {
    "add": "crear",
    "change": "editar",
    "delete": "eliminar",
    "view": "listar",
}

TRANSLATION_APP = {
    "accounts": "Usuarios",
    "admin": "Admin Django",
    "auth": "Autenticacion",
    "sessions": "Sesiones",
}

TRANSLATION_MODELS = {
    "group": "grupo",
    "permission": "permiso",
    "customuser": "usuarios",
    "logentry": "registros",
    "session": "sesiones"
}

def get_permissions():
    permissions = Permission.objects.select_related(
            "content_type"
        ).order_by("content_type__app_label", "codename")
        
    grouped_permissions = defaultdict(list)
    
    for permission in permissions:
        action, model = permission.codename.split("_", 1)
        
        permission.spanish_name = (
            "Puede "
            f"{TRANSLATIONS.get(action)} "
            f"{TRANSLATION_MODELS.get(model)}"
        )
        
        app_label = permission.content_type.app_label
        app_name = TRANSLATION_APP.get(app_label, None)
        
        if app_name:
            grouped_permissions[app_name].append(permission)
    
    return grouped_permissions


