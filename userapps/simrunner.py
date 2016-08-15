from opts import config
import discover
from objects.node import Node
from concurrent.futures import ProcessPoolExecutor

executor = ProcessPoolExecutor(5)


def prepare_nodes(nodes, config):
    def _prepare(node):
        """
        :type node: Node
        """
        try:
            node.sftp.mkdir('/tmp/oslo_bench')
            node.sftp.chdir('/tmp/oslo_bench')
            node.sftp.put('./scripts/prepare.sh', '/tmp/oslo_bench/prep.sh')
            print node.run('./prep.sh', split=False)
        except Exception as e:
            print e

    for node in nodes:
        _prepare(node)


def run_simulator(node, config):
    props = config.simulator_props
    topics = ["bench_topic.%s" % str(i) for i in range(props.topics)]


def main():
    nodes = discover.available(config)
    prepare_nodes(nodes, config)


main()
