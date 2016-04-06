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

class BaseStation(object):
    def __init__(self):
        self.xbee = pyflightcontrol.XBee(pyflightcontrol.XBee.findExplorerDev())
        self.acstate = pyflightcontrol.AircraftState()
        devs = pyflightcontrol.base.Joystick.autodetect()
        self.stick = devs['stick'][0]
        self.rudder = devs['rudder'][0]
        self._last_update = None

    def handleDownlink(self, pkt):
        self._last_update = pyflightcontrol.proto.Timestamp()
        self._last_update.MergeFrom(pkt.time)
        pkt_type = pkt.WhichOneof('uplink_type')
        if pkt_type == 'manual':
            self.acstate.quaternion.do_set(
                    pkt.sensors.ahrs.e0,
                    pkt.sensors.ahrs.ex,
                    pkt.sensors.ahrs.ey,
                    pkt.sensors.ahrs.ez)
            self.acstate.p = pkt.manual.static
            self.acstate.T = pkt.manual.temp

    @asyncio.coroutine
    def downlink_loop(self):
        while True:
            self.xbee.readPktAsync(pyflightcontrol.proto.command_downlink,
                    self.handleDownlink)
            yield from asyncio.sleep(0.04)

    @asyncio.coroutine
    def uplink_loop(self):
        while True:
            pkt = pyflightcontrol.proto.command_uplink()
            pkt.manual.d_a = stick.getX()*2.0*aileron_range/256 - elevator_range
            pkt.manual.d_e = stick.getY()*2.0*elevator_range/256 - elevator_range
            pkt.manual.d_r = rudder.getX()*2.0*rudder_range/256 - rudder_range
            pkt.manual.motor_pwr = stick.getZ()*100.0/256
            # Write Control Packet
            try:
                self.xbee.writePkt(pkt)
            except IOError as e:
                print(e)
            yield from asyncio.sleep(0.075)

    @asyncio.coroutine
    def render_loop(self):
        # Initialize GUI
        pygame.init()
        screensz = 1024
        screen = pygame.display.set_mode((screensz, screensz))
        pfd = pyflightcontrol.base.PFD(screensz, screensz)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise
            # Render display
            surf = pfd.render(self.acstate)
            screen.blit(surf, (0, 0))
            pygame.display.flip()
            yield from asyncio.sleep(0.1)
    
    def register(self):
        asyncio.async(self.render_loop)
        asyncio.async(self.uplink_loop)
        asyncio.async(self.downlink_loop)
        self.stick.register()
        self.rudder.register()

if __name__ == '__main__':
    b = BaseStation()
    b.register()
    loop = asyncio.get_event_loop()
    loop.start()
