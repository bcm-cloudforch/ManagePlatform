from django.db import models

# Create your models here.

class Host(models.Model):
    hostname = models.CharField(max_length=64)
    ip = models.GenericIPAddressField(protocol='ipv4', unique=True)
    api_port = models.PositiveIntegerField()
    docker_ver = models.CharField(max_length=64, null=True)
    disk_all = models.FloatField(null=True)
    disk_free = models.FloatField(null=True)
    mem_all = models.FloatField(null=True)
    mem_free = models.FloatField(null=True)
    password = models.CharField(max_length=64, null=True)
    os = models.CharField(max_length=64, default='CentOS 7', null=True)


class Container(models.Model):
    host = models.ForeignKey(to='Host',null=True, on_delete=models.SET_NULL)
    base_img = models.CharField(max_length=128, null=True)
    uuid = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=64)
    cmd = models.CharField(max_length=256, null=True)
    network = models.CharField(max_length=64)
    """
    容器的运行状态:
    {
    0: 'running',
    1: 'exited',
    2: 'created',
    3: 'restarting'
    }
    """
    status = models.SmallIntegerField()


class Image(models.Model):
    name = models.CharField(max_length=128)
    tag = models.CharField(max_length=64)
    host = models.ForeignKey(to='Registry', on_delete=models.CASCADE)

class Registry(models.Model):
    ip = models.GenericIPAddressField(protocol='ipv4', unique=True)
    port = models.IntegerField()
    hostname = models.CharField(max_length=128, null=True)
