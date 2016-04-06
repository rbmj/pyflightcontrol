from google.protobuf.timestamp_pb2 import Timestamp
import socket
import time
from . import util
from .daemon import DaemonServer

def mktimestamp():
    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 1e9)
    return Timestamp(seconds=seconds, nanos=nanos)

def gettm(tm):
    return tm.seconds + tm.nanos*1e-9

class RpcProtocol(object):
    def __init__(self, name, port, query_type, response_type, actions={}):
        self.name = name
        self.port = port
        self.query_type = query_type
        self.response_type = response_type
        self.actions = actions

    def addAction(self, qtype, action):
        self.actions[qtype] = action

class RpcServer(DaemonServer):
    def __init__(self, protocol):
        self.protocol = protocol
        super().__init__(protocol.port, protocol.name)

    def handle(self, conn):
        while True:
            query = self.protocol.query_type()
            if not conn.receiveBuffer(query):
                break
            qtype = query.WhichOneof('query_type')
            if qtype is not None:
                resp = self.protocol.response_type()
                resp.query_time.CopyFrom(query.time)
                resp_action = self.protocol.actions.get(qtype)
                if resp_action is None:
                    conn.log.info('Unrecognized query type ' + qtype)
                else:
                    try:
                        subq = getattr(query, qtype)
                        subr = getattr(resp, qtype)
                    except AttributeError:
                        conn.log.error('Bad Protocol Buffer for ' + qtype)
                    else:
                        resp_val = resp_action(subq, gettm(query.time))
                        if resp_val is None:
                            conn.log.info('Error processing action'
                                    + 'for type ' + qtype)
                        else:
                            subr.CopyFrom(resp_val)
            resp.time.MergeFrom(mktimestamp())
            conn.sendBuffer(resp)

class RpcClient(object):
    def __init__(self, host, protocol, log):
        self._host = host
        self.protocol = protocol
        self._sock = None
        self.log = log

    def connect(self):
        if not (self._sock is None):
            return
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._sock.connect((self._host, self.protocol.port))
        except Exception as e:
            self.log.exception(e)
            self.close()

    def close(self):
        if self._sock is None:
            return
        try:
            self._sock.close()
        except:
            pass
        self._sock = None

    def query(self, qtype, buf):
        q = self.protocol.query_type()
        q.time.CopyFrom(mktimestamp())
        try:
            subq = getattr(q, qtype)
        except AttributeError:
            self.log.error('Bad protocol buffer for ' + qtype)
            return None
        subq.CopyFrom(buf)
        self.connect()
        if self._sock is None:
            return None
        try:
            resp = self.protocol.response_type()
            util.sendBuffer(q, self._sock)
            if not util.receiveBuffer(resp, self._sock):
                self.log.error('Cannot receive query')
                return None
        except Exception as e:
            self.log.exception(e)
            self.close()
            return None
        if resp.WhichOneof('response_type') != qtype:
            self.log.warning('Bad response type')
            return None
        try:
            subr = getattr(resp, qtype)
        except AttributeError:
            self.log.error('Bad protocol buffer for ' + qtype)
            return None
        return (subr, gettm(resp.time))

