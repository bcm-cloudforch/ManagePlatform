# Generated by Django 2.0.5 on 2018-05-15 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dockermanage', '0006_auto_20180514_1404'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='host_to_img',
        ),
        migrations.AlterField(
            model_name='container',
            name='base_img',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
