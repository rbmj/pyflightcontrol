import pyflightcontrol
from usb import core
import threading
import serial
import ports
import time

from .mpl3115a2 import MPL3115A2
from .imu import IMU

class daq_vars(object):
    def __init__(self):
        self.p = 2117.0
        self.T = 460+50.0
        self.attitude = pyflightcontrol.math.Quaternion(0, 1, 0, 0)
        self.load = [0., 0., 1.]
        self.rot = [0., 0., 0.]
        self.mag = [0., 0., 0.]
        self.lock = threading.Lock()

class imu_thread(threading.Thread):
    def __init__(self, vars_out):
        self._vars = vars_out
        self.imu = IMU.create()

    def run(self):
        while True:
            self.imu.update()
            with self._vars.lock:
                self._vars.attitude.do_setq(self.imu.attitude)
                self._vars.load = list(*self.imu.accel)
                self._vars.rot = list(*self.imu.gyro)
                self._vars.mag = list(*self.imu.mag)

class pressure_thread(threading.Thread):
    def __init__(self, vars_out):
        self._vars = vars_out
        self.dev = MPL3115A2()
    
    def run(self):
        while True:
            self.dev.poll()
            with self._vars.lock:
                self._vars.p = self.dev.pressure
                self._vars.T = self.dev.temperature
            time.sleep(0.005)

def handle(connection):
    while True:
        cmd = daq_command()
        if not connection.receiveBuffer(cmd):
            break

class daq_daemon(pyflightcontrol.DaemonServer):
    def __init__(self):
        super().__init__(ports.tcpPort('daq'), 'daq', handle)

    def post_init(self):
        self._vars = daq_vars()
        t_imu = imu_thread(self._vars)
        t_imu.start()
        t_atmos = pressure_thread(self._vars)
        t_atmos.start()

    def handle(self, connection):
        while True:
            cmd = daq_command()
            if not connection.receiveBuffer(cmd):
                break
            outbuf = daq_resp()
            with self._vars.lock:
                outbuf.e0 = self._vars.attitude.e0
                # ...
            connection.sendBuffer(outbuf)

class DaqRpcChannel(pyflightcontrol.RpcChannel):
    def __init__(self):
        super().__init__(ports.tcpHost('daq'), ports.tcpPort('daq'))

    def getMeasurement(self):
        pass
