# Generated by Django 4.2.11 on 2024-04-23 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_webscrapping_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webscrapping',
            name='year',
            field=models.CharField(choices=[('ENERO', 'ENERO'), ('FEBRERO', 'FEBRERO'), ('MARZO', 'MARZO'), ('ABRIL', 'ABRIL'), ('MAYO', 'MAYO'), ('JUNIO', 'JUNIO'), ('JULIO', 'JULIO'), ('AGOSTO', 'AGOSTO'), ('SEPTIEMBRE', 'SEPTIEMBRE'), ('OCTUBRE', 'OCTUBRE'), ('NOVIEMBRE', 'NOVIEMBRE'), ('DICIEMBRE', 'DICIEMBRE')], default='ENERO', max_length=20),
        ),
    ]
