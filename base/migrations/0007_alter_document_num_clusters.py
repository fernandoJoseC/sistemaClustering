# Generated by Django 4.2.11 on 2024-04-15 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_alter_document_num_clusters'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='num_clusters',
            field=models.IntegerField(choices=[(2, '2'), (3, '3'), (4, '4'), (5, '5')], default=3),
        ),
    ]