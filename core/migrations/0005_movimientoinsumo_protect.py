from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_merge_20260819_1236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movimientoinsumo',
            name='insumo',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='movimientos',
                to='core.insumo',
            ),
        ),
    ]
