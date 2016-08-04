import six
import paramiko
from utils import print_list
from abc import abstractmethod, ABCMeta


@six.add_metaclass(ABCMeta)
class Service(object):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def restart(self, node):
        pass

    @abstractmethod
    def start(self, node):
        pass

    @abstractmethod
    def stop(self, node):
        pass


class Process(object):
    def __init__(self, node, user, pid, cmd):
        self.node = node
        self.user = user
        self.pid = pid
        self.cmd = cmd

    @classmethod
    def from_psaux_line(cls, line):
        line


class Node(object):
    def __init__(self, host, user, password=None, role='default'):
        self.host = host
        self.user = user
        self.password = password
        self.role = role
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(host, username=user, password=password)

    def run(self, cmd):
        sin, sout, serr = self.ssh.exec_command(cmd)
        return sout.readlines()

    def process_list(self):
        return self.run("ps -aux | awk '{print $1,$2,$3,$11}'")

    def service_list(self):
        return self.run('initctl list')

    def resource_list(self):
        pass


class OpenstackNode(Node):
    def __init__(self, **kwargs):
        super(OpenstackNode, self).__init__(**kwargs)

    def services_list(self):
        pass


@six.add_metaclass(ABCMeta)
class DiscoverBase(object):
    @abstractmethod
    def discover(self):
        """Return list of available nodes and roles"""
