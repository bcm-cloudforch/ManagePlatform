# Generated by Django 2.0.5 on 2018-05-15 07:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dockermanage', '0009_auto_20180515_0232'),
    ]

    operations = [
        migrations.RenameField(
            model_name='host',
            old_name='cpu',
            new_name='password',
        ),
        migrations.RemoveField(
            model_name='image',
            name='size',
        ),
    ]
