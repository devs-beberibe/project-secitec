from django.contrib import admin
from .models import (
    FichaDeManutencao,
    Componente,
    ComponenteEstado,
)

admin.site.register(FichaDeManutencao)
admin.site.register(Componente)
admin.site.register(ComponenteEstado)
