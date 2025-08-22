from django.db import migrations

def cargar_categorias_servicio(apps, schema_editor):
    ServiceCategory = apps.get_model('appointments', 'ServiceCategory')
    categorias = [
        ("🎨 Diseño Gráfico y Visual",),
        ("✏️ Ilustración y Arte Digital",),
        ("🎬 Animación y Video",),
        ("📹 Edición y Producción Audiovisual",),
        ("🎧 Audio y Sonido",),
        ("💻 Desarrollo Web y Programación",),
        ("🛒 E-commerce y Productos Digitales",),
        ("📱 Marketing Digital y Redes",),
        ("📚 Educación y Formación Digital",),
        ("✍️ Redacción, Textos y Traducción",),
        ("🔒 Ciberseguridad y Legal Digital",),
        ("🤝 Soporte y Gestión de Comunidades",),
    ]
    for nombre, in categorias:
        ServiceCategory.objects.get_or_create(name=nombre)

class Migration(migrations.Migration):
    dependencies = [('appointments', '0003_servicecategory'),]
    operations = [
        migrations.RunPython(cargar_categorias_servicio),
    ]
