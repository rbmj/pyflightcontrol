import proto.dolos_pb2
import time
import utils
import threading
import socket
import serial
from usb import core

# TODO: Stream resync on magic number 0xd0105acf

# Get XBee Device File - for SparkFun XBee Explorer
# This could be done less cruftily
snum = core.find(idVendor=0x0403, idProduct=0x6015).serial_number
prod = 'FTDI_FT231X_USB_UART'
dev = '/dev/serial/by-id/usb-{}_{}-if00-port0'.format(prod, snum)

class State(object):
    def __init__(self):
        self.aileron = 0.0
        self.elevator = 0.0
        self.rudder = 0.0
        self.motor = 0.0

state = utils.LockedWrapper(State())

def runClient():
    ser = serial.Serial(dev, baudrate=9600)
    while True:
        av = proto.dolos_pb2.actuation_vars()
        av.d_a = state.aileron
        av.d_e = state.elevator
        av.d_r = state.rudder
        av.motor_pwr = state.motor
        hb = utils.heartbeat_create()
        pkt = proto.dolos_pb2.control_packet()
        pkt.direct = av
        pkt.hb = hb
        utils.sendBuffer(pkt, ser)
        time.sleep(0.1)

clientThread = threading.Thread(target=runClient)
clientThread.start()

while True:
    cmd = input("> ").split()
    if len(cmd) != 2:
        print('Bad Syntax (CMD ARG)')
        continue
    try:
        if cmd[0] == 'aileron':
            state.aileron = float(cmd[1])
            continue
        if cmd[0] == 'elevator':
            state.elevator = float(cmd[1])
            continue
        if cmd[0] == 'rudder':
            state.elevator = float(cmd[1])
            continue
        if cmd[1] == 'motor':
            state.motor = float(cmd[1])
            continue
        print('Bad Command')
    except:
        print('Error')
