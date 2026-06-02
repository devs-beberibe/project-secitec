from django import forms
from .models import MaintenanceSheet, ComponentStatus


class MaintenanceSheetForm(forms.ModelForm):
    class Meta:
        model = MaintenanceSheet
        fields = "__all__"


class ComponentStatusForm(forms.ModelForm):
    class Meta:
        model = ComponentStatus
        fields = "__all__"
