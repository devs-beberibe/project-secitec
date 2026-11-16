from rest_framework.permissions import BasePermission


ADMINISTRATIVE_GROUP = "Administrativo"
TECHNICIAN_GROUP = "Tecnico"


def belongs_to(user, *group_names):
    return bool(
        user
        and user.is_authenticated
        and (
            user.is_superuser
            or user.groups.filter(name__in=group_names).exists()
        )
    )


class IsAdministrativeOrTechnician(BasePermission):
    message = "Acesso permitido aos grupos Administrativo e Tecnico."

    def has_permission(self, request, view):
        return belongs_to(
            request.user,
            ADMINISTRATIVE_GROUP,
            TECHNICIAN_GROUP,
        )


class IsTechnician(BasePermission):
    message = "Somente usuários do grupo Tecnico podem iniciar uma ficha."

    def has_permission(self, request, view):
        return belongs_to(request.user, TECHNICIAN_GROUP)
