import pyflightcontrol as pfc
import time
import threading
import socket
import serial
import asyncio
import pygame
from usb import core
from .PFD import PFD
import signal

@asyncio.coroutine
def main_loop(stick, rudder):
    # Get XBee Device File - for SparkFun XBee Explorer
    # This could be done less cruftily
    snum = core.find(idVendor=0x0403, idProduct=0x6015).serial_number
    prod = 'FTDI_FT231X_USB_UART'
    dev = '/dev/serial/by-id/usb-{}_{}-if00-port0'.format(prod, snum)
    
    # Initialize GUI
    pygame.init()
    screensz = 640
    screen = pygame.display.set_mode((screensz, screensz))
    pfd = PFD(screensz, screensz)
    ser = serial.Serial(dev, baudrate=9600)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise
        pkt = pfc.proto.control_packet()
        pkt.direct.d_a = stick.getX()
        pkt.direct.d_e = stick.getY()
        pkt.direct.d_r = rudder.getX()
        pkt.direct.motor_pwr = stick.getZ()
        pfc.util.heartbeat(pkt.hb)
        pfc.util.serialWriteBuffer(pkt, ser)
        pitch = stick.getY()*180.0/256 - 90
        roll = stick.getX()*180.0/256 - 90
        surf = pfd.render(0, pitch, roll)
        screen.blit(surf, (0, 0))
        pygame.display.flip()
        yield from asyncio.sleep(0.1)

def get_main_loop():
    devs = pfc.Joystick.autodetect()
    stick = devs['stick'][0]
    rudder = devs['rudder'][0]
    actions = []
    actions.append(asyncio.async(main_loop(stick, rudder)))
    actions.append(stick.register())
    actions.append(rudder.register())
    return (asyncio.get_event_loop(), actions)
