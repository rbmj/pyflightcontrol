import proto.dolos_pb2
import time
import utils
import threading
import socket
import serial
import ports
from usb import core

# TODO: Use RPi Serial Port
# Get XBee Device File - for SparkFun XBee Explorer
# This could be done less cruftily
snum = core.find(idVendor=0x0403, idProduct=0x6015).serial_number
prod = 'FTDI_FT231X_USB_UART'
dev = '/dev/serial/by-id/usb-{}_{}-if00-port0'.format(prod, snum)
ser = serial.Serial(dev, baudrate=9600)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(ports.tcpTuple('actuate'))
sockf = sock.makefile(mode='rwb')

while True:
    try:
        pkt = proto.dolos_pb2.control_packet()
        if pkt.HasField('direct'):
            acpkt = proto.dolos_pb2.actuation_packet()
            acpkt.direct.d_a = pkt.direct.d_a
            acpkt.direct.d_e = pkt.direct.d_e
            acpkt.direct.d_r = pkt.direct.d_r
            acpkt.direct.motor_pwr = pkt.direct.motor_pwr
            utils.sendBuffer(acpkt, sockf)
    except Exception as e:
        print(e)
