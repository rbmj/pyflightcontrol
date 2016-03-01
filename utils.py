import struct
import threading
import time
from proto import dolos_pb2

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

def heartbeat(hb):
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

class Shim(object):
    pass

class LockedWrapper(Shim):
    def __init__(self, wrapped):
        super(Shim, self).__setattr__('wrapped', wrapped)
        super(Shim, self).__setattr__('lock', threading.Lock())
    
    def __getattr__(self, attr):
        with self.lock:
            return getattr(self.wrapped, attr)

    def __setattr__(self, attr, value):
        with self.lock:
            return self.wrapped.__setattr__(attr, value)
