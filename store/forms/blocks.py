# store/forms/blocks.py

from django import forms

# 1. Formulario para bloque Hero
class HeroBlockForm(forms.Form):
    title = forms.CharField(label="Título", max_length=255)
    subtitle = forms.CharField(label="Subtítulo", max_length=255, required=False)
    background_image = forms.ImageField(label="Imagen de fondo (recomendado 1920x600)", required=False)
    cta_text = forms.CharField(label="Texto del botón", max_length=100, required=False)
    cta_url = forms.URLField(label="URL del botón", required=False)


# 2. Formulario para bloque Sobre mí
class AboutBlockForm(forms.Form):
    title = forms.CharField(label="Título", max_length=255)
    content = forms.CharField(label="Contenido", widget=forms.Textarea)
    image = forms.URLField(label="URL de la imagen", required=False)


# 3. Formulario para bloque de Productos destacados
class ProductsBlockForm(forms.Form):
    title = forms.CharField(label="Título", max_length=255, required=False)
    show_categories = forms.BooleanField(label="Mostrar categorías", required=False, initial=True)


# 4. Formulario para bloque de Testimonios
class TestimonialBlockForm(forms.Form):
    quote = forms.CharField(label="Testimonio", widget=forms.Textarea)
    author = forms.CharField(label="Autor del testimonio", max_length=100)
    image = forms.URLField(label="Imagen del autor", required=False)


# 5. Formulario para bloque de Contacto
class ContactBlockForm(forms.Form):
    title = forms.CharField(label="Título del formulario", max_length=255)
    show_phone = forms.BooleanField(label="¿Mostrar campo teléfono?", required=False)
    success_message = forms.CharField(label="Mensaje de éxito", max_length=255, required=False)


# 6. Diccionario centralizado que mapea el tipo de bloque con su formulario
BLOCK_FORM_MAP = {
    "hero": HeroBlockForm,
    "about": AboutBlockForm,
    "products": ProductsBlockForm,
    "testimonial": TestimonialBlockForm,
    "contact": ContactBlockForm,
}


# 7. Función opcional: obtener campos renderizables dinámicamente en templates
def get_block_fields(block_type):
    form_class = BLOCK_FORM_MAP.get(block_type)
    if not form_class:
        return []
    return form_class().fields.items()
