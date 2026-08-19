from django import forms
from core.models import Prestamo

class PrestamoForm(forms.ModelForm):

    class Meta:
        model = Prestamo
        fields = [
            "alumno",
            "docente",
            "herramienta",
        ]