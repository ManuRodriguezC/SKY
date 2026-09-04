from collections import defaultdict

from django.contrib.auth.models import Permission


MODEL_PERMISSIONS = {
    "group": [
        "add",
        "change",
        "delete",
        "view",
    ],
    "permission": [
        "add",
        "change",
        "delete",
        "view",
    ],
    "customuser": [
        "add",
        "change",
        "delete",
        "view",
    ],
    "automation": [
        "add",
        "change",
        "delete",
        "view",
        "execute",
        "test",
    ],
    "customer": [
        "add",
        "change",
        "delete",
        "view",
    ],
    "importexecution": [
        "import",
        "import",
    ],
}


TRANSLATIONS = {
    "add": "crear",
    "change": "editar",
    "delete": "eliminar",
    "view": "listar",
    "execute": "ejecutar",
    "test": "probar",
    "import": "importar",
}


TRANSLATION_APP = {
    "accounts": "Usuarios",
    "automations": "Automatizaciones",
    "admin": "Admin Django",
    "auth": "Autenticacion",
    "sessions": "Sesiones",
    "customers": "Asociados",
}


TRANSLATION_MODELS = {
    "group": "grupo",
    "permission": "permiso",
    "customuser": "usuarios",
    "logentry": "registros",
    "session": "sesiones",
    "automation": "automatizacion",
    "customer": "asociados",
    "importexecution": "asociados y obligaciones",
}


def get_permissions():
    permissions = (
        Permission.objects
        .select_related("content_type")
        .order_by(
            "content_type__app_label",
            "codename",
        )
    )
    grouped_permissions = defaultdict(list)

    for permission in permissions:
        model = permission.content_type.model

        allowed_permissions = MODEL_PERMISSIONS.get(
            model
        )

        if not allowed_permissions:
            continue

        if permission.codename in allowed_permissions:
            permission_name = permission.codename
        else:
            action, separator, _ = permission.codename.partition("_")

            if not separator or action not in allowed_permissions:
                continue

            permission_name = action

        permission.spanish_name = (
            "Puede "
            f"{TRANSLATIONS.get(permission_name, permission_name)} "
            f"{TRANSLATION_MODELS.get(model, model)}"
        )

        app_label = permission.content_type.app_label

        app_name = TRANSLATION_APP.get(
            app_label
        )

        if app_name:
            grouped_permissions[app_name].append(
                permission
            )

    return grouped_permissions