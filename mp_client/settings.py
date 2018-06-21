# -*- coding: utf-8 -*-
from dockermanage import models

HOST_LIST = models.Host.objects.all().values('ip', 'api_port')

API_LSIT = []
for i in HOST_LIST:
    API_LSIT.append(i.ip + i.api_port)

