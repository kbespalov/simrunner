from utils import print_list
from discover import OpenstackNode, Node
import unittest


class NodesTest(unittest.TestCase):
    def setUp(self):
        self.node = Node('localhost', 'kbespalov', '181093')

    def test_list_process(self):
        print_list('Processes', self.node.process_list())
