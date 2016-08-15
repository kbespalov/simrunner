import os

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
