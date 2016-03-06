import proto.dolos_pb2
import time
import utils
import threading
import socket
import serial
import asyncio
from usb import core
from Joystick import Joystick

# TODO: Stream resync on magic number 
# Get XBee Device File - for SparkFun XBee Explorer
# This could be done less cruftily
snum = core.find(idVendor=0x0403, idProduct=0x6015).serial_number
prod = 'FTDI_FT231X_USB_UART'
dev = '/dev/serial/by-id/usb-{}_{}-if00-port0'.format(prod, snum)

devs = Joystick.autodetect()
stick = devs['stick'][0]
rudder = devs['rudder'][0]
stick.register()
rudder.register()

@asyncio.coroutine
def main_loop():
    ser = serial.Serial(dev, baudrate=9600)
    while True:
        pkt = proto.dolos_pb2.control_packet()
        pkt.direct.d_a = stick.getX()
        pkt.direct.d_e = stick.getY()
        pkt.direct.d_r = rudder.getX()
        pkt.direct.motor_pwr = stick.getZ()
        utils.heartbeat(pkt.hb)
        utils.serialWriteBuffer(pkt, ser)
        yield from asyncio.sleep(0.1)

asyncio.async(main_loop)
loop = asyncio.get_event_loop()
loop.run_forever()
