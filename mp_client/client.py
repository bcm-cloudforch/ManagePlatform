# -*- coding: utf-8 -*-

# import psutil, platform
# mem = psutil.virtual_memory()
# mem_all = round(mem.total/1024/1024/1024, 2)
# mem_free = round(mem.free/1024/1024/1024, 2)
#
# disk = psutil.disk_usage('/')
# disk_all = round(disk.total/1024/1024/1024, 2)
# disk_free = round(disk.free/1024/1024/1024, 2)
#
# os = platform.platform().split('-')[-3:-1]

from dockermanage import models
import docker

HOST_LIST = models.Host.objects.all().values('ip', 'api_port')

API_LIST = []
for i in HOST_LIST:
    API_LIST.append(i.ip + i.api_port)

for item in HOST_LIST:
    api = "tcp://" + item.ip + ":" + item.api_port
    stats = {}
    client = docker.APIClient(base_url=item)
    stats['os'] = client.info()['OperatingSystem']
    stats['docker_ver'] = client.version()['Version']
    models.Host.objects.filter(ip=item.ip).update(**stats)

