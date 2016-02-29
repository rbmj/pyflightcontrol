import struct
import threading

def readBuffer(protobuf, sock):
    msg = sock.read(2)
    if msg[0] == 0xFF and msg[1] == 0xFF:
        return None
    l = struct.unpack('!H', msg)[0]
    msg = sock.read(l)
    return protobuf.ParseFromString(msg)

def sendBuffer(protobuf, sock):
    msg = protobuf.SerializeToString()
    l = struct.pack('!H', len(msg))
    sock.write(l+msg)

def sendClose(sock):
    sock.write(bytes('\xff\xff', 'latin_1'))

def heartbeat_create():
    hb = proto.dolos_pb2.heartbeat()
    tm = time.time()
    epoch = int(tm)
    hb.millis = int(tm*1000) % 1000
    hb.epoch_low = epoch & 0xFFFFFFFF
    hb.epoch_hi = epoch >> 32
    return hb

def heartbeat_gettime(hb):
    epoch = (hb.epoch_hi << 32) | hb.epoch_low
    frac = float(hb.millis)/1000
    return epoch+frac


class LockedWrapper(object):
    def __init__(self, wrapped):
        self.wrapped = wrapped
        self.lock = threading.Lock()
    
    def __getattr__(self, attr):
        with self.lock:
            getattr(self.wrapped, attr)

    def __setattr__(self, attr, value):
        with self.lock:
            setattr(self.wrapped, attr, value)
