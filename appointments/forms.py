from django import forms
from .models import Service, AvailabilitySlot

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'description', 'duration_minutes', 'price', 'is_active']


class AvailabilitySlotForm(forms.ModelForm):
    class Meta:
        model = AvailabilitySlot
        fields = ['weekday', 'start_time', 'end_time']
