from abc import abstractmethod, ABCMeta
from yaml import load, dump

import six

from objects.node import FuelMasterNode, Node


def parse_ssh_url(url):
    credentials, host = url.split("@")
    user, password = credentials.split(":")
    return host, user, password


@six.add_metaclass(ABCMeta)
class DiscoverBase(object):
    @abstractmethod
    def discover(self):
        """Return list of available nodes and roles"""


class ManualDiscover(DiscoverBase):
    def __init__(self, cfg):
        self.cfg = cfg.discover_file

    def discover(self):
        nodes = []
        with open(self.cfg.file) as config:
            hosts = load(config)
            for role, role_hosts in hosts.iteritems():
                for host in role_hosts:
                    nodes.append(Node(*parse_ssh_url(host)))
            return nodes


class FuelDiscover(DiscoverBase):
    _cache = {}

    def __init__(self, master_node):
        if master_node not in self._cache:
            self.master_node = FuelMasterNode(*parse_ssh_url(master_node))
        else:
            self.master_node = self._cache[master_node]

    def discover(self):
        nodes = []
        nodes.extend(self.master_node.fuel_controllers())
        nodes.extend(self.master_node.fuel_compute())
        return nodes


def available(cfg):
    modes = {'manual': ManualDiscover, 'fuel': FuelDiscover}
    mode = cfg.discover_mode
    return modes[mode](cfg).discover()
