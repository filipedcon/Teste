# Generated by Django 5.1.7 on 2025-03-30 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('operadoras', '0005_alter_operadora_bairro_alter_operadora_cep_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operadora',
            name='Registro_ANS',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
