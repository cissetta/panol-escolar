from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_movimientoinsumo_protect'),
    ]

    operations = [
        migrations.AddField(
            model_name='herramienta',
            name='tipo',
            field=models.CharField(
                choices=[('HERRAMIENTA', 'Herramienta'), ('MAQUINA', 'Máquina')],
                default='HERRAMIENTA',
                max_length=12,
                verbose_name='Tipo',
            ),
        ),
        migrations.AddField(
            model_name='herramienta',
            name='imagen',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='herramientas/',
                verbose_name='Imagen',
            ),
        ),
        migrations.AddField(
            model_name='insumo',
            name='imagen',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='insumos/',
                verbose_name='Imagen',
            ),
        ),
    ]
