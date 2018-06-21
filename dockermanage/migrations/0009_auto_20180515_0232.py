# Generated by Django 2.0.5 on 2018-05-15 02:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dockermanage', '0008_auto_20180515_0202'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registry',
            name='host',
        ),
        migrations.AddField(
            model_name='registry',
            name='hostname',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='registry',
            name='ip',
            field=models.GenericIPAddressField(default='192.168.16.100', protocol='ipv4', unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registry',
            name='port',
            field=models.IntegerField(default=5000),
            preserve_default=False,
        ),
    ]
