from django import forms

from appointments.utils import generar_horas_disponibles
from .models import Service, AvailabilitySlot

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'description', 'duration_minutes', 'price', 'is_active']

class AvailabilitySlotForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        duracion = kwargs.pop('duracion', 30)  # Por defecto 30 min si no se pasa nada
        super().__init__(*args, **kwargs)

        # Reemplazamos los campos start_time y end_time por selects
        self.fields['start_time'] = forms.ChoiceField(
            choices=generar_horas_disponibles(duracion),
            label="Hora de inicio"
        )
        self.fields['end_time'] = forms.ChoiceField(
            choices=generar_horas_disponibles(duracion),
            label="Hora de fin"
        )

    class Meta:
        model = AvailabilitySlot
        fields = ['weekday', 'start_time', 'end_time']
