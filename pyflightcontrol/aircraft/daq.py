import pyflightcontrol
from usb import core
import threading
import serial
import time

from .mpl3115a2 import MPL3115A2
from .imu import IMU

class daq_vars(object):
    def __init__(self):
        self.p = 2117.0
        self.T = 460+50.0
        self.attitude = pyflightcontrol.angle.Quaternion(0, 1, 0, 0)
        self.load = [0., 0., 1.]
        self.rot = [0., 0., 0.]
        self.mag = [0., 0., 0.]
        self.lock = threading.Lock()

class imu_thread(threading.Thread):
    def __init__(self, vars_out):
        self._vars = vars_out
        self.imu = IMU.create()
        super().__init__()

    def run(self):
        while True:
            self.imu.update()
            with self._vars.lock:
                self._vars.attitude.do_setq(self.imu.attitude)
                self._vars.load = list(self.imu.accel)
                self._vars.rot = list(self.imu.gyro)
                self._vars.mag = list(self.imu.mag)

class atmos_thread(threading.Thread):
    def __init__(self, vars_out):
        self._vars = vars_out
        self.dev = MPL3115A2()
        super().__init__()
    
    def run(self):
        while True:
            self.dev.poll()
            with self._vars.lock:
                self._vars.p = self.dev.pressure
                self._vars.T = self.dev.temperature
            time.sleep(0.005)

Protocol = pyflightcontrol.system.RpcProtocol('daq',
        pyflightcontrol.ports.tcpPort('daq'),
        pyflightcontrol.proto.daq_query,
        pyflightcontrol.proto.daq_response)

class Server(pyflightcontrol.system.RpcServer):
    def __init__(self):
        self._vars = daq_vars()
        t_imu = imu_thread(self._vars)
        t_imu.start()
        t_atmos = atmos_thread(self._vars)
        t_atmos.start()
        protocol = Protocol
        protocol.addAction('measure', self.handleMeasure)
        super().__init__(protocol)

    def handleMeasure(self, flag, timestamp):
        pkt = pyflightcontrol.proto.sensor_measurement()
        with self._vars.lock:
            pkt.ahrs.e0 = self._vars.attitude.e0
            pkt.ahrs.ex = self._vars.attitude.ex
            pkt.ahrs.ey = self._vars.attitude.ey
            pkt.ahrs.ez = self._vars.attitude.ez
            pkt.accel.nx = self._vars.load[0]
            pkt.accel.ny = self._vars.load[1]
            pkt.accel.nz = self._vars.load[2]
            pkt.gyro.p = self._vars.rot[0]
            pkt.gyro.q = self._vars.rot[1]
            pkt.gyro.r = self._vars.rot[2]
            pkt.magneto.mx = self._vars.mag[0]
            pkt.magneto.my = self._vars.mag[1]
            pkt.magneto.mz = self._vars.mag[2]
            pkt.static = self._vars.p
            pkt.temp = self._vars.T
        return pkt

class Client(pyflightcontrol.system.RpcClient):
    def __init__(self, log):
        super().__init__(pyflightcontrol.ports.tcpHost('daq'), 
                Protocol, log)

    def measure(self):
        pkt = pyflightcontrol.proto.bool_wrap()
        pkt.value = True;
        ret = self.query('measure', pkt)
        return ret

if __name__ == '__main__':
    srv = Server()
    srv.startDaemon()
