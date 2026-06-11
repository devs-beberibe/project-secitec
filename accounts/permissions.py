from rest_framework.permissions import BasePermission


class IsAdministracao(BasePermission):
    message = "Apenas Administração pode acessar esta rota."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.groups.filter(name="Administracao").exists()
            )
        )


class IsTecnico(BasePermission):
    message = "Apenas Técnicos podem acessar esta rota."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.groups.filter(name__startswith="Tecnico").exists()
            )
        )
