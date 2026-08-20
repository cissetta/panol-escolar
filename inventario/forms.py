from django import forms

from core.models import (
    Categoria,
    Herramienta,
    Insumo,
    MovimientoInsumo,
)


# =========================================================
# CATEGORÍA
# =========================================================

class CategoriaForm(forms.ModelForm):

    class Meta:
        model = Categoria
        fields = [
            "nombre",
            "descripcion",
            "color_hex",
        ]

        labels = {
            "nombre": "Nombre",
            "descripcion": "Descripción",
            "color_hex": "Color",
        }

        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre de la categoría",
                }
            ),

            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descripción",
                }
            ),

            "color_hex": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "type": "color",
                }
            ),
        }


# =========================================================
# HERRAMIENTA
# =========================================================

class HerramientaForm(forms.ModelForm):

    class Meta:
        model = Herramienta

        fields = [
            "codigo",
            "nombre",
            "descripcion",
            "marca",
            "modelo",
            "categoria",
            "ubicacion",
            "estado",
            "fecha_compra",
            "costo",
        ]

        labels = {
            "codigo": "Código",
            "nombre": "Nombre",
            "descripcion": "Descripción",
            "marca": "Marca",
            "modelo": "Modelo",
            "categoria": "Categoría",
            "ubicacion": "Ubicación",
            "estado": "Estado",
            "fecha_compra": "Fecha de compra",
            "costo": "Costo",
        }

        widgets = {

            "codigo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Se genera automáticamente",
                }
            ),

            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre de la herramienta",
                }
            ),

            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descripción de la herramienta",
                }
            ),

            "marca": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Marca",
                }
            ),

            "modelo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Modelo",
                }
            ),

            "categoria": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "ubicacion": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ejemplo: Estante 1",
                }
            ),

            "estado": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "fecha_compra": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "costo": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Costo",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Estado inicial para una herramienta nueva
        if not self.instance.pk:
            self.fields["estado"].initial = "DISPONIBLE"


# =========================================================
# INSUMO
# =========================================================

class InsumoForm(forms.ModelForm):

    class Meta:
        model = Insumo

        fields = [
            "codigo",
            "nombre",
            "descripcion",
            "categoria",
            "unidad",
            "stock_actual",
            "stock_minimo",
        ]

        labels = {
            "codigo": "Código",
            "nombre": "Nombre",
            "descripcion": "Descripción",
            "categoria": "Categoría",
            "unidad": "Unidad",
            "stock_actual": "Stock actual",
            "stock_minimo": "Stock mínimo",
        }


# =========================================================
# MOVIMIENTO DE INSUMO
# =========================================================

class MovimientoInsumoForm(forms.ModelForm):

    class Meta:
        model = MovimientoInsumo
        fields = [
            "insumo",
            "tipo",
            "cantidad",
            "observacion",
        ]

        labels = {
            "insumo": "Insumo",
            "tipo": "Tipo de movimiento",
            "cantidad": "Cantidad",
            "observacion": "Observación",
        }