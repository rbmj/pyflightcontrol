import struct

def readBuffer(protobuf, sock):
    msg = sock.recv(2)
    if msg[0] == 0xFF and msg[1] == 0xFF:
        return None
    l = struct.unpack('!H', msg)[0]
    msg = sock.recv(l)
    return protobuf.ParseFromString(msg)

def sendBuffer(protobuf, sock):
    msg = protobuf.SerializeToString()
    l = struct.pack('!H', len(msg))
    sock.send(l+msg)

def sendClose(sock):
    sock.send(bytes('\xff\xff', 'latin_1'))
