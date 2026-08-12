from django import forms
from core.models import Alumno

class AlumnoForm(forms.ModelForm):
    # Campo visual para igualar el diseño (no se guarda en la BD porque no existe)
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales...'})
    )

    class Meta:
        model = Alumno
        fields = ['nombre', 'apellido', 'dni', 'curso', 'email']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            # Dejamos que Django arme el menú desplegable con las opciones oficiales del modelo, 
            # nosotros solo le agregamos la clase de Bootstrap para que se vea bien:
            'curso': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'alumno@escuela.edu.ar'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacemos que el email sea realmente opcional para que Django no bloquee el guardado
        self.fields['email'].required = False  

    def clean_dni(self):
        dni = self.cleaned_data.get('dni', '').strip()
        if not dni.isdigit():
            raise forms.ValidationError('El DNI debe contener solo números.')
        
        # Validación de DNI único excluyendo al propio alumno durante la edición
        qs = Alumno.objects.filter(dni=dni)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f'Ya existe un alumno con DNI {dni}.')
        return dni