# Generated by Django 4.1.3 on 2022-11-15 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pci', '0004_data_cargos_data_inscricoes_ate_data_nivel'),
    ]

    operations = [
        migrations.AddField(
            model_name='data',
            name='vagas',
            field=models.CharField(default='', max_length=50),
        ),
    ]
