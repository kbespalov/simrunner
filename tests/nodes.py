from utils import print_list
from discover import OpenstackNode, Node, Process
import unittest


class NodesTest(unittest.TestCase):
    def setUp(self):
        self.node = Node('localhost', 'kbespalov', '181093')

    def test_list_process(self):
        print_list('Processes', self.node.process_list())

    def test_list_configs(self):

        cmds = [
            "/usr/bin/python2.7 /usr/bin/neutron-dhcp-agent --config-file=/etc/neutron/neutron.conf "
            "--config-file=/etc/neutron/dhcp_agent.ini",
            "/usr/bin/python /usr/bin/heat-engine --config-file=/etc/heat/heat.conf",
            "/usr/bin/python2.7 /usr/bin/neutron-metadata-agent --config-file=/etc/neutron/neutron.conf "
            "--config-file=/etc/neutron/metadata_agent.ini"
        ]

        a = Process(None, None, None, cmds[0])
        b = Process(None, None, None, cmds[1])
        c = Process(None, None, None, cmds[2])

        print a.list_configs()
        print b.list_configs()
        print c.list_configs()
