import proto.dolos_pb2
import time
import utils
import threading
import socket
import serial
import asyncio
import pygame
from usb import core
from Joystick import Joystick
from PFD import PFD

import signal

# Get XBee Device File - for SparkFun XBee Explorer
# This could be done less cruftily
snum = core.find(idVendor=0x0403, idProduct=0x6015).serial_number
prod = 'FTDI_FT231X_USB_UART'
dev = '/dev/serial/by-id/usb-{}_{}-if00-port0'.format(prod, snum)

actions = []

devs = Joystick.autodetect()
stick = devs['stick'][0]
rudder = devs['rudder'][0]
actions.append(stick.register())
actions.append(rudder.register())

pygame.init()
screensz = 320
screen = pygame.display.set_mode((screensz, screensz))
pfd = PFD(screensz, screensz)

@asyncio.coroutine
def main_loop():
    ser = serial.Serial(dev, baudrate=9600)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise
        pkt = proto.dolos_pb2.control_packet()
        pkt.direct.d_a = stick.getX()
        pkt.direct.d_e = stick.getY()
        pkt.direct.d_r = rudder.getX()
        pkt.direct.motor_pwr = stick.getZ()
        utils.heartbeat(pkt.hb)
        utils.serialWriteBuffer(pkt, ser)
        pitch = (stick.getY()*180.0/256 - 90)
        roll = stick.getX()*180.0/256 - 90
        print('setting to {}:{}'.format(pitch, roll))
        surf = pfd.render(pitch, roll)
        screen.blit(surf, (0, 0))
        pygame.display.flip()
        yield from asyncio.sleep(0.1)

actions.append(asyncio.async(main_loop()))
loop = asyncio.get_event_loop()

try:
    loop.run_forever()
finally:
    for act in actions:
        act.cancel()
    pygame.quit()
    loop.close()
