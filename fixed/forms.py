from django import forms
from .models import FichaDeManutencao, ComponenteEstado


class FichaDeManutencaoForm(forms.ModelForm):
    class Meta:
        model = FichaDeManutencao
        fields = "__all__"


class ComponenteEstadoForm(forms.ModelForm):
    class Meta:
        model = ComponenteEstado
        fields = "__all__"
