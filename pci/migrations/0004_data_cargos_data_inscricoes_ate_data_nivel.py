# Generated by Django 4.1.3 on 2022-11-15 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pci', '0003_data_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='data',
            name='cargos',
            field=models.CharField(default='', max_length=400),
        ),
        migrations.AddField(
            model_name='data',
            name='inscricoes_ate',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='data',
            name='nivel',
            field=models.CharField(default='', max_length=50),
        ),
    ]
