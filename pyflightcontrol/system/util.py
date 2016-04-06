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

def receiveBuffer(protobuf, sock):
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

def sendClose(sock):
    sock.sendall(bytes('\xff\xff', 'latin_1'))

