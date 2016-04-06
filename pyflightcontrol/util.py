import struct
import threading
import time

def sock_recvall(sock, n):
    data = bytes()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def readBuffer(protobuf, sock):
    msg = sock_recvall(sock, 2)
    if msg[0] == 0xFF and msg[1] == 0xFF:
        return False
    l = struct.unpack('!H', msg)[0]
    msg = sock_recvall(sock, l)
    protobuf.ParseFromString(msg)
    return True

def sendBuffer(protobuf, sock):
    msg = protobuf.SerializeToString()
    l = struct.pack('!H', len(msg))
    sock.sendall(l+msg)

serialMagic = struct.pack('!I', 0xd0105acf)

def serialReadBuffer(protobuf, ser):
    # Stream resynchronization
    buf = 'AAAA'.encode('ascii')
    while buf != serialMagic:
        buf = buf[1:] + ser.read(1)
    # Read length
    l = struct.unpack('!H', ser.read(2))[0]
    buf = ser.read(l)
    return protobuf.ParseFromString(buf)

def serialWriteBuffer(protobuf, ser):
    msg = protobuf.SerializeToString()
    ser.write(serialMagic + struct.pack('!H', len(msg)) + msg)

def sendClose(sock):
    sock.sendall(bytes('\xff\xff', 'latin_1'))

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
