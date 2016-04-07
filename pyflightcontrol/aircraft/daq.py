import pyflightcontrol
from usb import core
import threading
import serial
import time

from .mpl3115a2 import MPL3115A2
from .imu import IMU

class imu_thread(threading.Thread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.imu = IMU.create()

    def run(self):
        while True:
            self.imu.update()
            self.parent.set_attitude(self.imu.attitude)
            self.parent.set_imu(
                    list(self.imu.accel),
                    list(self.imu.gyro),
                    list(self.imu.mag))

class atmos_thread(threading.Thread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.dev = MPL3115A2()
    
    def run(self):
        while True:
            self.dev.poll()
            self.parent.set_atmos(self.dev.pressure, self.dev.temperature)
            time.sleep(0.01)

Protocol = pyflightcontrol.system.RpcProtocol('daq',
        pyflightcontrol.ports.tcpPort('daq'),
        pyflightcontrol.proto.daq_query,
        pyflightcontrol.proto.daq_response)

class Server(pyflightcontrol.system.RpcServer):
    def __init__(self):
        protocol = Protocol
        protocol.addAction('measure', self.handleMeasure)
        super().__init__(protocol)

    def post_init(self):
        self.p = 2117.0
        self.T = 460+50.0
        self.attitude = pyflightcontrol.angle.Quaternion(0, 1, 0, 0)
        self.load = [0., 0., 1.]
        self.rot = [0., 0., 0.]
        self.mag = [0., 0., 0.]
        self.lock = threading.Lock()
        self.t_imu = imu_thread(self)
        self.t_imu.start()
        self.t_atmos = atmos_thread(self)
        self.t_atmos.start()

    def set_attitude(self, quat):
        with self.lock:
            self.attitude.do_setq(quat)

    def set_imu(self, accel, gyro, mag):
        with self.lock:
            self.load = accel
            self.rot = gyro
            self.mag = mag

    def set_atmos(self, pressure, temperature):
        with self.lock:
            self.p = pressure
            self.T = temperature

    def handleMeasure(self, flag, timestamp):
        pkt = pyflightcontrol.proto.sensor_measurement()
        with self.lock:
            pkt.ahrs.e0 = float(self.attitude.e0)
            pkt.ahrs.ex = float(self.attitude.ex)
            pkt.ahrs.ey = float(self.attitude.ey)
            pkt.ahrs.ez = float(self.attitude.ez)
            pkt.accel.nx = self.load[0]
            pkt.accel.ny = self.load[1]
            pkt.accel.nz = self.load[2]
            pkt.gyro.p = self.rot[0]
            pkt.gyro.q = self.rot[1]
            pkt.gyro.r = self.rot[2]
            pkt.magneto.mx = self.mag[0]
            pkt.magneto.my = self.mag[1]
            pkt.magneto.mz = self.mag[2]
            pkt.static = self.p
            pkt.temp = self.T
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
