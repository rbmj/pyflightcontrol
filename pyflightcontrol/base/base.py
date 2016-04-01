import pyflightcontrol
import pyflightcontrol.base
import google.protobuf
import time
import threading
import socket
import serial
import asyncio
import pygame
from usb import core
import signal

rudder_range = 30
aileron_range = 30
elevator_range = 30

acstate = pyflightcontrol.AircraftState

def procpkt(pkt):
    # process aircraft telemetry data

@asyncio.coroutine
def main_loop(stick, rudder):
    # Initialize GUI
    pygame.init()
    screensz = 1024
    screen = pygame.display.set_mode((screensz, screensz))
    pfd = pyflightcontrol.base.PFD(screensz, screensz)
    xbee = pyflightcontrol.XBee(pyflightcontrol.XBee.findExplorerDev())
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise
        pkt = pyflightcontrol.proto.control_packet()
        pkt.direct.d_a = stick.getX()*2.0*aileron_range/256 - elevator_range
        pkt.direct.d_e = stick.getY()*2.0*elevator_range/256 - elevator_range
        pkt.direct.d_r = rudder.getX()*2.0*rudder_range/256 - rudder_range
        pkt.direct.motor_pwr = stick.getZ()*100.0/256
        pyflightcontrol.util.heartbeat(pkt.hb)
        # Write Control Packet
        try:
            xbee.writePkt(pkt)
        except IOError as e:
            print(e)
        # Read Telemetry Packet, if received
        try:
            xbee.readPktAsync(pyflightcontrol.proto.telemetry_packet, procpkt)
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
    devs = pyflightcontrol.base.Joystick.autodetect()
    stick = devs['stick'][0]
    rudder = devs['rudder'][0]
    actions = []
    actions.append(asyncio.async(main_loop(stick, rudder)))
    actions.append(stick.register())
    actions.append(rudder.register())
    return (asyncio.get_event_loop(), actions)
