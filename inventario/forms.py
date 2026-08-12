from django import forms

from core.models import (
    Categoria,
    Herramienta,
    Insumo,
    MovimientoInsumo,
)


class CategoriaForm(forms.ModelForm):

    class Meta:
        model = Categoria
        fields = "__all__"


class HerramientaForm(forms.ModelForm):

    class Meta:
        model = Herramienta
        fields = "__all__"


class InsumoForm(forms.ModelForm):

    class Meta:
        model = Insumo
        fields = "__all__"


class MovimientoInsumoForm(forms.ModelForm):

    class Meta:
        model = MovimientoInsumo
        fields = "__all__"