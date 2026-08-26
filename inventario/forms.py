from django import forms

from core.models import (
    Alumno,
    Categoria,
    Docente,
    Herramienta,
    Insumo,
    MovimientoInsumo,
    PrestamoInsumo,
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
            "unidad",
            "stock_actual",
            "stock_minimo",
        ]

        labels = {
            "codigo": "Código",
            "nombre": "Nombre",
            "descripcion": "Descripción",
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

        widgets = {
            "insumo": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "tipo": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "cantidad": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.01",
                }
            ),
            "observacion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }


# =========================================================
# ENTREGA DE INSUMO
# =========================================================

class EntregaInsumoForm(forms.ModelForm):

    TIPO_ENTREGA = [
        ('alumno', 'Entrega a alumno'),
        ('ajuste', 'Ajuste manual'),
    ]

    tipo_entrega = forms.ChoiceField(
        choices=TIPO_ENTREGA,
        label='Tipo de movimiento',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'tipo_entrega_select'})
    )

    class Meta:
        model = PrestamoInsumo
        fields = [
            "alumno",
            "insumo",
            "docente",
            "cantidad",
            "observacion",
        ]

        labels = {
            "alumno": "Alumno",
            "insumo": "Insumo",
            "docente": "Docente",
            "cantidad": "Cantidad",
            "observacion": "Observación",
        }

        widgets = {
            "alumno": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "alumno_field"
                }
            ),
            "insumo": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "docente": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "docente_field"
                }
            ),
            "cantidad": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.01",
                }
            ),
            "observacion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases de Bootstrap a todos los campos
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'attrs'):
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'

        # Hacer el campo de alumno opcional para ajustes manuales
        self.fields['alumno'].required = False