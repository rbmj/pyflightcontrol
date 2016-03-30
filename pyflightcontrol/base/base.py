import pyflightcontrol as pfc
import google.protobuf
import time
import threading
import socket
import serial
import asyncio
import pygame
from usb import core
from .PFD import PFD
import signal

rudder_range = 30
aileron_range = 30
elevator_range = 30

acstate = pfc.AircraftState

def procpkt(pkt):
    # process aircraft telemetry data

@asyncio.coroutine
def main_loop(stick, rudder):
    # Initialize GUI
    pygame.init()
    screensz = 1024
    screen = pygame.display.set_mode((screensz, screensz))
    pfd = PFD(screensz, screensz)
    xbee = pfc.XBee(pfc.XBee.findExplorerDev())
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise
        pkt = pfc.proto.control_packet()
        pkt.direct.d_a = stick.getX()*2.0*aileron_range/256 - elevator_range
        pkt.direct.d_e = stick.getY()*2.0*elevator_range/256 - elevator_range
        pkt.direct.d_r = rudder.getX()*2.0*rudder_range/256 - rudder_range
        pkt.direct.motor_pwr = stick.getZ()*100.0/256
        pfc.util.heartbeat(pkt.hb)
        # Write Control Packet
        try:
            xbee.writePkt(pkt)
        except IOError as e:
            print(e)
        # Read Telemetry Packet, if received
        try:
            xbee.readPktAsync(pfc.proto.telemetry_packet, procpkt)
        except google.protobuf.message.DecodeError as de:
            print(de)
        except IOError as ioe:
            print(ioe)
        # Render display
        surf = pfd.render(acstate)
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
