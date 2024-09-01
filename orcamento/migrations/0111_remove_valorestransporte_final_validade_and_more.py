from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orcamento', '0110_orcamentoopicional_valor_final'),
    ]

    operations = [
        migrations.RenameField(
            model_name='valorestransporte',
            old_name='inicio_validade',
            new_name='inicio_vigencia',
        ),
        migrations.RenameField(
            model_name='valorestransporte',
            old_name='final_validade',
            new_name='final_vigencia',
        ),
    ]
