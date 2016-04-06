from .rpc import RpcProtocol, RpcServer, RpcClient
from .daemon import DaemonConnection, DaemonServer
from . import test_pb2 as proto
from .test_server import TestProtocol
from datetime import datetime
import logging

class TestClient(RpcClient):
    def __init__(self):
        super().__init__('127.0.0.1', TestProtocol, logging)

    def echo(self, s):
        pkt = proto.str()
        pkt.value = s
        ret = self.query('echo', pkt)
        if ret is None:
            return None
        return (ret[0].value, ret[1])

if __name__ == '__main__':
    queries = ['foobarbaz', 'quux']
    client = TestClient()
    for q in queries:
        ret = client.echo(q)
        if ret is None:
            print('Sent {}, no response'.format(q))
        else:
            resp = ret[0]
            tm = datetime.fromtimestamp(ret[1])
            print('Sent {}, received {} at {}'.format(q, resp, tm))

