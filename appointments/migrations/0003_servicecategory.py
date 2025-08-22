from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('appointments', '0002_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='ServiceCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('icon', models.CharField(max_length=50, blank=True, null=True)),
            ],
        ),
    ]
