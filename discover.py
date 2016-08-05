import functools
import os

import six
import paramiko
from abc import abstractmethod, ABCMeta

from concurrent.futures import ThreadPoolExecutor
from oslo_log import log
from utils import retry

LOG = log.getLogger(__name__)


class Process(object):
    def __init__(self, node, user, pid, cmd):
        self.node = node
        self.user = user
        self.pid = pid
        self.cmd = cmd
        self.executable = self._executable()

    def _executable(self):
        if self.cmd.startswith('['):
            return self.cmd
        else:
            os.path.basename(self.cmd.split(" ")[0])

    @retry(5, lambda e: LOG.error("Failed to restart process %s" % e))
    def restart(self):
        LOG.info("Restarting process %s on %s" % (self.executable, self.node.host))
        self.node.ssh.exec_command("kill %s" % self.cmd)
        self.node.ssh.exec_command(self.cmd)

    @classmethod
    def from_psaux_line(cls, node, line):

        pos_a = line.find(" ") + 1
        pos_b = line.find(" ", pos_a) + 1

        user = line[:pos_a].rstrip()
        pid = line[pos_a:pos_b].rstrip()
        cmd = line[pos_b:].rstrip()

        return cls(node, user, pid, cmd)

    def _parse_args_files(self, filematch):
        """ Match files like configs /etc/*.conf or logs /var/log/*.log"""
        files, start_pos = [], 0
        while True:
            pos_a = self.cmd.find(filematch, start_pos)
            if pos_a > 0:
                pos_b = self.cmd.find(' ', pos_a)
                if pos_b > 0:
                    files.append(self.cmd[pos_a:pos_b])
                else:
                    files.append(self.cmd[pos_a:])
                start_pos = pos_b
            else:
                return files

    def list_configs(self):
        return self._parse_args_files('/etc/')

    def list_logs(self):
        return self._parse_args_files('/var/log/')

    def __str__(self):
        return "user: %s pid: %s executable: %s" % (self.user, self.pid, self.executable)


class Node(object):
    # used for running async jobs
    _pool = ThreadPoolExecutor(8)

    def __init__(self, host, user, password=None, role='default'):
        self.host = host
        self.user = user
        self.password = password
        self.role = role
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(host, username=user, password=password)

    def run(self, cmd, split=True):
        sin, sout, serr = self.ssh.exec_command(cmd)
        if split:
            return [line.rstrip() for line in sout.readlines()]
        else:
            return sout.read()

    def list_process(self):
        process_list = []
        raw_result = self.run("ps -xo user,pid,cmd | sort -u")
        for psaux_line in raw_result[1:]:
            process_list.append(Process.from_psaux_line(self, psaux_line))
        return process_list

    @staticmethod
    def retry_with_log(attempts, fail_msg):
        return functools.partial(attempts, lambda e: LOG.error(fail_msg))

    @retry(5, lambda e: LOG.error("Failed to get ip address of interface %s" % e))
    def get_interface_ip(self, interface_name):
        return self.run("ifconfig %s | grep 'inet addr' | awk -F: '{print $2}' | awk '{print $1}'" % interface_name)

    @retry(5, lambda e: LOG.error("Failed to get list of services %s" % e))
    def list_service(self):
        return self.run('initctl list | awk "{print $1}"| sort -u')

    @retry(5, lambda e: LOG.error("Failed to get list of resources %s" % e))
    def list_resource(self):
        return self.run('crm_resource --list-raw')

    @retry(5, lambda e: LOG.error("Failed to restart service %s" % e))
    def restart_service(self, name):
        return self.run("service %s restart" % name)

    @retry(5, lambda e: LOG.error("Failed to restart resource %s" % e))
    def restart_resource(self, name):
        return self.run("crm resource restart %s " % name)

    @retry(5, lambda e: LOG.error("Failed to restart process %s" % e))
    def restart_process(self, process):
        return process.restart()

    def read_file(self, location):
        return self.run()


class OpenstackNode(Node):
    KEYWORDS = {
        'nova',
        'neutron',
        'cinder',
        'keystone',
        'glance',
        'swift',
        'sahara',
        'ceilometer',
        'heat',
        'aodh'
    }

    def __init__(self, *args, **kwargs):
        super(OpenstackNode, self).__init__(*args, **kwargs)

    def list_openstack_services(self):
        services = set()
        for service in self.list_service():
            for key in self.KEYWORDS:
                if key in service:
                    services.add(service)
                    break
        return services

    def list_openstack_process(self):
        processes = set()
        for process in self.list_process():
            for key in self.KEYWORDS:
                if key in process.cmd:
                    processes.add(process)
                    break
        return processes

    def list_openstack_resources(self):
        resources = set()
        if self.role != 'controller':
            return resources
        for resource in self.list_resource():
            for key in self.KEYWORDS:
                if key in resource.cmd:
                    resource.add(resource)
                    break
        return resources


class FuelMasterNode(Node):
    def fuel_controllers(self):
        nodes = []
        hosts = self.run("fuel nodes 2>&1 | grep controller | awk -F '|' '{ print $5 }'")
        for ip in hosts:
            nodes.append(OpenstackNode(ip, 'root', role='controller'))
        return nodes

    def fuel_computes(self):
        nodes = []
        hosts = self.run("fuel nodes 2>&1 | grep compute | awk -F '|' '{ print $5 }'")
        for ip in hosts:
            nodes.append(OpenstackNode(ip, 'root', role='compute'))
        return nodes


@six.add_metaclass(ABCMeta)
class DiscoverBase(object):
    @abstractmethod
    def discover(self):
        """Return list of available nodes and roles"""
