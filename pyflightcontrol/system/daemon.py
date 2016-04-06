from . import util
import daemon
from daemon.pidfile import PIDLockFile
import socket
import signal
import threading
import logging
import logging.handlers

class DaemonConnection(threading.Thread):
    def __init__(self, sock, log, remote, srv):
        super().__init__()
        self.sock = sock
        self.log = log
        self.remote = remote
        self._srv = srv

    def run(self):
        try:
            self._srv.handle(self)
        except Exception as e:
            self.log.exception(e)
        finally:
            self.sock.close()

    def sendBuffer(self, buf):
        return util.sendBuffer(buf, self.sock)

    def receiveBuffer(self, buf):
        return util.receiveBuffer(buf, self.sock)


class DaemonServer(object):
    def __init__(self, port, name):
        self._name = name
        self._fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._fd.bind(('0.0.0.0', port))
        self._fd.listen(5)

        self._context = daemon.DaemonContext(
                working_directory='/var/lib',
                umask=0o002,
                pidfile=PIDLockFile('/var/run/pfc-' + name + '.pid'),
                detach_process=True
        )
        self._context.signal_map = {
            signal.SIGTERM:  'terminate'
        }
        #context.gid = grp.getgrnam('foo').gr_gid
        self._context.files_preserve = [self._fd]

    def preserve_file(self, f):
        self._context.files_preserve.append(f)

    def map_signal(self, signum, sighnd):
        self._context.signal_map[signum] = sighnd

    # Override this method to do post-fork initialization
    def post_init(self):
        pass

    # Override this method to handle connections
    def handle(self, connection):
        pass

    def startDaemon(self):
        self._log = logging.getLogger('pfc-' + self._name)
        loghnd = logging.handlers.SysLogHandler(address='/dev/log')
        self._log.addHandler(loghnd)
        try:
            with self._context:
                self._main()
        except Exception as e:
            self._log.exception(e)

    def start(self):
        self._log = logging
        try:
            self._main()
        except Exception as e:
            self._log.exception(e)

    def _main(self):
        self.post_init()
        while True:
            (sock, addr) = self._fd.accept()
            conn = DaemonConnection(sock, self._log, addr, self)
            conn.start()
