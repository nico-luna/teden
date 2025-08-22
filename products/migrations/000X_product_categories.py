from django.db import migrations

def cargar_categorias_producto(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    categorias = [
        ("Plantillas & Herramientas",),
        ("Ebooks & Guías",),
        ("Presets & Plugins",),
        ("Cursos & Mini Cursos",),
        ("Recursos Creativos",),
        ("Audios & Música",),
        ("Fotografía de Stock",),
        ("Inteligencia Artificial",),
        ("NFTs & Criptomonedas",),
        ("Licencias & Accesos",),
        ("Videojuegos",),
    ]
    for nombre, in categorias:
        Category.objects.get_or_create(name=nombre)

class Migration(migrations.Migration):
    dependencies = [('products', '0002_initial'),]
    operations = [
        migrations.RunPython(cargar_categorias_producto),
    ]
