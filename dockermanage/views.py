from django.shortcuts import render, HttpResponse
from django.views import View
from dockermanage import models
import docker
import json
import threading
import paramiko
import requests
import time

CTN_STATUS={
    0: 'running',
    1: 'exited',
    2: 'created',
    3: 'restarting'
}

CTN_REV_STATUS= {key:value for value,key in CTN_STATUS.items() }


# Create your views here.

class Overview(View):
    def get(self, request):
        host_obj_list = models.Host.objects.all()
        host_list = []
        for i in host_obj_list:
            host_list.append({
                'hostname': i.hostname,
                'api': "tcp://" + str(i.ip) + ":" + str(i.api_port),
                'mem_per': str(int((i.mem_free / i.mem_all) * 100)) + "%",
                'mem_str': int((i.mem_free / i.mem_all) * 100),
                'disk_per': str(int((i.disk_free / i.disk_all) * 100)) + "%",
                'disk_str': int((i.disk_free / i.disk_all) * 100)
            })
        return render(request, 'overview.html', {"host_obj": host_list})

class Hosts(View):

    def get(self, request):
        host_list = []
        host_obj_list = models.Host.objects.all()
        for i in host_obj_list:
            host_list.append({ 'ip': i.ip, 'hostname': i.hostname,
                               'api_port': i.api_port, 'docker_ver': i.docker_ver,
                               'disk_all': i.disk_all,
                               'disk_free': i.disk_free,
                               'mem_all': i.mem_all,
                               'mem_free': i.mem_free,
                               'os': i.os, 'id': i.id})
        return render(request, 'hosts.html', {"host_obj": host_list})

# 主机创建&修改
def ajax_host_mod(request):
    ret = {'status': True, 'error': None, 'data': None}
    hostname = request.POST.get('hostname')
    ip = request.POST.get('ip')
    api_port = request.POST.get('api_port')
    id = request.POST.get('id')
    if len(id) != 0:
        data_new = {'id': request.POST.get('id'), 'hostname': hostname,
                    'ip': ip, 'api_port': api_port}
        try:
            models.Host.objects.filter(id=id).update(**data_new)
        except:
            ret['status'] = False
            ret['error'] = 'Update DB Error!'
    else:
        try:
            models.Host.objects.create(hostname=hostname, ip=ip, api_port=api_port)
            UpdateHost(ip, api_port).start()
        except:
            ret['status'] = False
            ret['error'] = 'DB Inserting Error!'
    return HttpResponse(json.dumps(ret))

# 主机删除
def ajax_host_del(request):
    ret = {'status': True, 'error': None, 'data': None}
    id = request.POST.get('id')
    try:
        models.Host.objects.filter(id=id).delete()
    except:
        ret['status'] = False
        ret['error'] = 'DB Deleting Error!'
    return HttpResponse(json.dumps(ret))


class Containers(View):

    def get(self, request):
        result = []
        host = models.Host.objects.all()
        for i in host:
            ctn_dict = {}
            ctn_dict['hostname'] = i.hostname
            ctn_dict['hostid'] = i.id
            ctn_dict['hostip'] = i.ip
            ctn_dict['ctn'] = models.Container.objects.filter(host_id=i.id)
            result.append(ctn_dict)
        return render(request, 'containers.html', {'ctn_obj': result})

class Images(View):

    def get(self, request):
        result = []
        registry = models.Registry.objects.all()
        for i in registry:
            img_dict = {}
            img_dict['registry'] = i.hostname + ":" + str(i.port)
            img_dict['img'] = models.Image.objects.filter(host_id=i.id)
            result.append(img_dict)
        return render(request, 'images.html', {'img_obj': result})

class containerAction(View):

    def post(self, request):
        ret = {"status": True, "error": None, "data": None}
        act_dict = {
            'start': self.containerStart,
            'stop': self.containerStop,
            'restart': self.containerRestart,
            'destroy': self.containerDestroy
        }
        ctn_id = request.POST.get('ctn_id')
        host_id = request.POST.get('host_id')
        action = request.POST.get('action')
        ctn_uuid = models.Container.objects.filter(id=ctn_id).first().uuid
        host_obj = models.Host.objects.filter(id=host_id).first()
        host_ip, host_port = host_obj.ip, host_obj.api_port
        api = "tcp://" + str(host_ip) + ":" + str(host_port)
        client = docker.APIClient(base_url=api)
        result = act_dict[action](client, ctn_uuid)
        #UpdateContainer(host_ip, host_port).run()
        if result:
            ret['status'] = False
            ret['error'] = result
        return HttpResponse(json.dumps(ret))

    def containerStart(self, client, ctn):
        return client.start(container=ctn)

    def containerStop(self, client, ctn):
        return client.stop(container=ctn, timeout=60)

    def containerRestart(self, client, ctn):
        return client.restart(container=ctn)

    def containerDestroy(self, client, ctn):
        return client.remove_container(container=ctn, force=True)







################
# 后台数据刷新
################
class UpdateHost(threading.Thread):
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.docker_api = "tcp://" + str(self.ip) + ":" + str(self.port)
        self.reg_api = "http://" + str(self.ip) + ":" + str(self.port) + '/v2/'

    def run(self):
        while True:
            stats = {}
            password = models.Host.objects.filter(ip=self.ip).first().password

            try:
                client = paramiko.SSHClient()
                client.load_system_host_keys()
                client.connect(hostname=self.ip, username='root', password=password)
                a, b, c = client.exec_command('df')
                disk_used, disk_free = b.read().decode().split()[9:11]
                disk_all = float(disk_free) + float(disk_used)
                stats['disk_all'] = round(disk_all / (1024 * 1024), 2)
                stats['disk_free'] = round(float(disk_free) / (1024 * 1024), 2)
                a, b, c = client.exec_command('free')
                mem = b.read().decode().split()
                mem_all, mem_free = mem[7], mem[12]
                stats['mem_all'] = round(float(mem_all) / (1024 * 1024), 2)
                stats['mem_free'] = round(float(mem_free) / (1024 * 1024), 2)

            except ConnectionError as e:
                print('SSH Connection %s timeout!' % self.ip)

            try:
                client = docker.APIClient(base_url=self.docker_api)
                stats['os'] = client.info()['OperatingSystem']
                stats['docker_ver'] = client.version()['Version']
            except requests.exceptions.ConnectTimeout as e:
                print('Docker Connecting %s timeout!' % self.docker_api)
            models.Host.objects.filter(ip=self.ip).update(**stats)

            time.sleep(60)

class UpdateContainer(threading.Thread):
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.docker_api = "tcp://" + str(self.ip) + ":" + str(self.port)
        self.reg_api = "http://" + str(self.ip) + ":" + str(self.port) + '/v2/'

    def run(self):
        while True:

            try:
                client = docker.APIClient(base_url=self.docker_api)
                ctn_list = client.containers(all=True)
                ctn_uuid_host = []
                for i in ctn_list:
                    ctn_uuid_host.append(i['Id'])
                    if models.Container.objects.filter(uuid=i['Id']).first():
                        models.Container.objects.filter(uuid=i['Id']).update(
                            name=i['Names'][0][1:],
                            network=i['NetworkSettings']['Networks']['bridge']['IPAddress'],
                            base_img=i['Image'],
                            cmd=i['Command'],
                            host_id=models.Host.objects.filter(ip=self.ip).first().id,
                            status=CTN_REV_STATUS[i['State']]
                        )
                    else:
                        models.Container.objects.create(
                            uuid=i['Id'],
                            name=i['Names'][0][1:],
                            network=i['NetworkSettings']['Networks']['bridge']['IPAddress'],
                            base_img=i['Image'],
                            cmd=i['Command'],
                            host_id=models.Host.objects.filter(ip=self.ip).first().id,
                            status=CTN_REV_STATUS[i['State']]
                        )

            except requests.exceptions.ConnectTimeout as e:
                print('Docker Connecting %s timeout!' % self.docker_api)
            else:
                ctn_uuid_db = []
                obj = models.Container.objects.filter(host_id=models.Host.objects.filter(ip=self.ip).first().id)
                for i in obj:
                    ctn_uuid_db.append(i.uuid)
                for i in ctn_uuid_db:
                    if i not in ctn_uuid_host:
                        models.Container.objects.filter(uuid=i).delete()

            finally:
                time.sleep(30)

class UpdateImage(threading.Thread):
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.docker_api = "tcp://" + str(self.ip) + ":" + str(self.port)
        self.reg_api = "http://" + str(self.ip) + ":" + str(self.port) + '/v2/'

    def run(self):
        while True:

            img_tag = []
            host_id = models.Registry.objects.filter(ip=self.ip).first().id
            res = requests.get(self.reg_api + '_catalog')
            img_list = json.loads(res.text)['repositories']

            for i in img_list:
                res = requests.get(self.reg_api + '%s/tags/list' % i)
                res = json.loads(res.text)
                res['ip'] = self.ip
                img_tag.append(res)

            for i in img_tag:
                if models.Image.objects.filter(host_id=host_id, name=i['name']).first():
                    models.Image.objects.filter(host_id=host_id, name=i['name']).update(tag=i['tags'])
                else:
                    models.Image.objects.create(name=i['name'], tag=i['tags'], host_id=host_id)

            time.sleep(60)

HOST_LIST = models.Host.objects.all().values('ip', 'api_port')
REG_LIST = models.Registry.objects.all().values('ip', 'port')
for i in HOST_LIST:
    UpdateHost(i['ip'], i['api_port']).start()
    UpdateContainer(i['ip'], i['api_port']).start()
for i in REG_LIST:
    UpdateImage(i['ip'], i['port']).start()

def callUpdateContainer(request):
    host_id = request.POST.get('host_id')
    host_obj = models.Host.objects.filter(id=host_id).first()
    host_ip, host_port = host_obj.ip, host_obj.api_port
    UpdateContainer(host_ip, host_port).run()