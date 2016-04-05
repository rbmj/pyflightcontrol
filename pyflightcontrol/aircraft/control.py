import pyflightcontrol
import proto.dolos_pb2
import time
import utils
import threading
import socket
import serial
import ports
from usb import core

xbee = pyflightcontrol.XBee(pyflightcontrol.XBee.findRPiSerialDev())

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(ports.tcpTuple('actuate'))

while True:
#    try:
        pkt = proto.dolos_pb2.control_packet()
        utils.serialReadBuffer(pkt, ser)
        if pkt.HasField('direct'):
            print('Received direct control packet')
            print('\tDa {} De {} Dr {} M {}'.format(
                pkt.direct.d_a, pkt.direct.d_e,
                pkt.direct.d_r, pkt.direct.motor_pwr))
            acpkt = proto.dolos_pb2.actuation_packet()
            acpkt.direct.d_a = pkt.direct.d_a
            acpkt.direct.d_e = pkt.direct.d_e
            acpkt.direct.d_r = pkt.direct.d_r
            acpkt.direct.motor_pwr = pkt.direct.motor_pwr
            print('\tDa {} De {} Dr {} M {}'.format(
                acpkt.direct.d_a, acpkt.direct.d_e,
                acpkt.direct.d_r, acpkt.direct.motor_pwr))
            utils.sendBuffer(acpkt, sock)
#    except Exception as e:
#        print(e)
