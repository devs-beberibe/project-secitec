from django import forms
from .models import Call


class CallForm(forms.ModelForm):
    class Meta:
        model = Call
        fields = ["secretary_sector", "problem", "requester"]
