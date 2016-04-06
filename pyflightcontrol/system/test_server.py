from .rpc import RpcProtocol, RpcServer, RpcClient
from .daemon import DaemonConnection, DaemonServer
from . import test_pb2 as proto
from datetime import datetime

TestProtocol = RpcProtocol('test', 5555, proto.test_query, 
        proto.test_response)

class TestServer(RpcServer):
    def __init__(self):
        protocol = TestProtocol
        protocol.addAction('echo', self.handleEcho)
        super().__init__(protocol)

    def handleEcho(self, echo_str, timestamp):
        tm = datetime.fromtimestamp(timestamp)
        s = echo_str.value
        print('received {} at time {}'.format(s, tm))
        pkt = proto.str()
        pkt.value = s
        return pkt

if __name__ == '__main__':
    srv = TestServer()
    srv.startDaemon()

