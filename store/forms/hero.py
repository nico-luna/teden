from django import forms

class HeroBlockForm(forms.Form):
    title = forms.CharField(label="Título", max_length=255)
    subtitle = forms.CharField(label="Subtítulo", max_length=255, required=False)
    background_image = forms.URLField(label="Imagen de fondo", required=False)
    cta_text = forms.CharField(label="Texto del botón", max_length=100, required=False)
    cta_url = forms.URLField(label="URL del botón", required=False)