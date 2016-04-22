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
import sys

#FIXME: full servo deflection, no calibration.  should be done on server
rudder_range = 90
aileron_range = 90
elevator_range = 90

class BaseStation(object):
    def __init__(self):
        self.xbee = pyflightcontrol.XBee(pyflightcontrol.XBee.findExplorerDev())
        self.acstate = pyflightcontrol.AircraftState()
        devs = pyflightcontrol.base.Joystick.autodetect()
        t = devs['stick']
        self.stick = t[0] if t else None
        if not (self.stick is None):
            self.stick.invertZ()
        t = devs['rudder']
        self.rudder = t[0] if t else None
        self._last_update = None

    def handleDownlink(self, pkt):
        self._last_update = pyflightcontrol.proto.Timestamp()
        self._last_update.MergeFrom(pkt.time)
        pkt_type = pkt.WhichOneof('downlink_type')
        #print('received downlink packet: {} bytes'.format(pkt.ByteSize()))
        if pkt_type == 'manual':
            self.acstate.quaternion = pyflightcontrol.angle.Quaternion(
                    pkt.manual.sensors.ahrs.e0,
                    pkt.manual.sensors.ahrs.ex,
                    pkt.manual.sensors.ahrs.ey,
                    pkt.manual.sensors.ahrs.ez)
            #print('\tAttitude {:2.1f}:{:2.1f}:{:2.1f} mode {}'.format(
            #    self.acstate.euler.pitch_d,
            #    self.acstate.euler.roll_d,
            #    self.acstate.euler.bearing_d,
            #    pkt.manual.sensors.ahrs.mode))
            self.acstate.p = pkt.manual.sensors.static
            self.acstate.T = pkt.manual.sensors.temp

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
            if not (self.stick is None):
                self.acstate.aileron = self.stick.getX()*2.0*aileron_range/256 - aileron_range
                pkt.manual.d_a = self.acstate.aileron
                self.acstate.elevator = self.stick.getY()*2.0*elevator_range/256 - elevator_range
                pkt.manual.d_e = self.acstate.elevator
                z = self.stick.getZ()
                self.acstate.motor = z*100.0/256
                pkt.manual.motor_pwr = self.acstate.motor
            if not (self.rudder is None):
                self.acstate.rudder = self.rudder.getX()*2.0*rudder_range/256 - rudder_range
                pkt.manual.d_r = self.acstate.rudder
            print('Sending {}:{}:{}:{}'.format(pkt.manual.d_a, pkt.manual.d_e,
                pkt.manual.d_r, pkt.manual.motor_pwr))
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
                    sys.exit(0)
            # Render display
            surf = pfd.render(self.acstate)
            screen.blit(surf, (0, 0))
            pygame.display.flip()
            yield from asyncio.sleep(0.1)
    
    def register(self):
        asyncio.async(self.render_loop())
        asyncio.async(self.uplink_loop())
        asyncio.async(self.downlink_loop())
        if self.stick:
            self.stick.register()
        if self.rudder:
            self.rudder.register()

    def exception_handler(self, loop, context):
        #FIXME: This doesn't actually reap the errors, why?
        #       still get exception traces on exit
        if isinstance(context.get('exception'), SystemExit):
            return
        loop.default_exception_handler(context)

if __name__ == '__main__':
    b = BaseStation()
    b.register()
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except SystemExit:
        loop.close()
        pass
