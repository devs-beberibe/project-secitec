from django.contrib import admin
from .models import (
    FichaVerificacaoComponentes,
    Componente,
    ComponenteEstado,
)

admin.site.register(FichaVerificacaoComponentes)
admin.site.register(Componente)
admin.site.register(ComponenteEstado)
