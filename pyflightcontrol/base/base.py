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
import evdev

aileron_range = pyflightcontrol.ports.aileron_range
elevator_range = pyflightcontrol.ports.elevator_range
rudder_range = pyflightcontrol.ports.rudder_range

def smooth(cmd, old, gain_min, gain_max):
    delta = abs(cmd - old)
    gain = (gain_max - gain_min)*delta + gain_min
    return gain*cmd + (1-gain)*old

class BaseStation(object):
    def __init__(self):
        self.xbee = pyflightcontrol.XBee(pyflightcontrol.XBee.findExplorerDev())
        self.acstate = pyflightcontrol.AircraftState()
        #devs = pyflightcontrol.base.Joystick.autodetect()
        #t = devs['stick']
        #self.stick = t[0] if t else None
        self.stick = pyflightcontrol.base.Joystick('/dev/input/by-id/usb-Saitek_Saitek_X52_Flight_Control_System-event-joystick')
        if not (self.stick is None):
            self.stick.invertZ()
            self.stick.addButtonHandler(self.zeroalt, evdev.ecodes.ecodes['BTN_THUMB'])
        #t = devs['rudder']
        #self.rudder = t[0] if t else None
        self.rudder = None
        self._last_update = None
        self._stickaxes = [0, 0, 0]
        self._telemfile = open('telemetry.out', 'wb')
        self._ctrlfile = open('controls.out', 'wb')
        self._trim = [0, 0, 0]

    def zeroalt(self):
        self.acstate.setrawqnh(self.acstate.p)
        print('ZEROING ALTIMETER')

    def handleDownlink(self, pkt):
        self._last_update = pyflightcontrol.proto.Timestamp()
        self._last_update.MergeFrom(pkt.time)
        pkt_type = pkt.WhichOneof('downlink_type')
        try:
            self._telemfile.write(pkt.SerializeToString())
        except:
            pass
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
                self._trim[0] = self._trim[0] - 0.02*self.stick.getHAT0X()
                self._trim[1] = self._trim[1] - 0.02*self.stick.getHAT0Y()
                self._trim[2] = self._trim[2] + 0.02*(
                        self.stick.getButton(evdev.ecodes.BTN_TRIGGER_HAPPY3) -
                        self.stick.getButton(evdev.ecodes.BTN_TRIGGER_HAPPY1))
                for i in range(len(self._trim)):
                    if self._trim[i] > 0.5:
                        self._trim[i] = 0.5
                    if self._trim[i] < -0.5:
                        self._trim[i] = -0.5
                ail_cmd = 2048 - self.stick.getX()
                ail_cmd = ail_cmd*2/2048.0 - 1
                ail_cmd = ail_cmd + self._trim[0]
                ail_cmd = smooth(ail_cmd, self._stickaxes[0], 0.75, 1.0)
                el_cmd = 2048 - self.stick.getY()
                el_cmd = el_cmd*2/2048.0 - 1
                el_cmd = el_cmd + self._trim[1]
                el_cmd = smooth(el_cmd, self._stickaxes[1], 0.75, 1.0)
                rud_cmd = 1 - self.stick.getRZ()*2/1024.0
                rud_cmd = rud_cmd + self._trim[2]
                rud_cmd = smooth(rud_cmd, self._stickaxes[2], 0.75, 1.0)
                if abs(ail_cmd) > 1:
                    ail_cmd = ail_cmd/abs(ail_cmd)
                if abs(el_cmd) > 1:
                    el_cmd = el_cmd/abs(el_cmd)
                if abs(rud_cmd) > 1:
                    rud_cmd = rud_cmd/abs(rud_cmd)
                if ail_cmd > 0:
                    self.acstate.aileron = aileron_range[1]*ail_cmd
                else:
                    self.acstate.aileron = aileron_range[0]*abs(ail_cmd)
                if el_cmd > 0:
                    self.acstate.elevator = elevator_range[1]*el_cmd
                else:
                    self.acstate.elevator = elevator_range[0]*abs(el_cmd)
                if rud_cmd > 0:
                    self.acstate.rudder = rudder_range[1]*rud_cmd
                else:
                    self.acstate.rudder = rudder_range[0]*abs(rud_cmd)
                ail_cmd = round(ail_cmd, 2)
                el_cmd = round(el_cmd, 2)
                rud_cmd = round(rud_cmd, 2)
                self._stickaxes[0] = ail_cmd
                self._stickaxes[1] = el_cmd
                self._stickaxes[2] = rud_cmd
                pkt.manual.d_a = self.acstate.aileron
                pkt.manual.d_e = self.acstate.elevator
                pkt.manual.d_r = self.acstate.rudder
                z = self.stick.getZ()
                self.acstate.motor = z*100.0/256
                pkt.manual.motor_pwr = self.acstate.motor
            if not (self.rudder is None):
                rud_cmd = self.rudder.getX()*2/256 - 1
                rud_cmd = smooth(rud_cmd, self._stickaxes[2], 0.75, 1.0)
                if rud_cmd > 0:
                    self.acstate.rudder = rudder_range[1]*rud_cmd
                else:
                    self.acstate.rudder = rudder_range[0]*abs(rud_cmd)
                pkt.manual.d_r = self.acstate.rudder
            print('Sending {:2.2f}:{:2.2f}:{:2.2f}:{:2.2f}'.format(pkt.manual.d_a, pkt.manual.d_e,
                pkt.manual.d_r, pkt.manual.motor_pwr))
            # Write Control Packet
            try:
                self.xbee.writePkt(pkt)
            except IOError as e:
                print(e)
            # Write controls to disk
            try:
                self._ctrlfile.write(pkt.SerializeToString())
            except:
                pass
            yield from asyncio.sleep(0.075)

    @asyncio.coroutine
    def render_loop(self):
        # Initialize GUI
        pygame.init()
        screensz = 1600
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
