# Generated by Django 4.2.11 on 2024-04-10 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_document_num_clusters'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='num_clusters',
            field=models.IntegerField(default='3', max_length=1),
        ),
    ]
