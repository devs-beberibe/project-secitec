from django import forms
from .models import FichaVerificacaoComponentes, ComponenteEstado


class FichaVerificacaoComponentesForm(forms.ModelForm):
    class Meta:
        model = FichaVerificacaoComponentes
        fields = "__all__"


class ComponenteEstadoForm(forms.ModelForm):
    class Meta:
        model = ComponenteEstado
        fields = "__all__"
