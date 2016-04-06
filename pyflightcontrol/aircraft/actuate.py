import pyflightcontrol
from usb import core
from .maestro import Maestro
import threading

def getPWM(deg):
    # units are in quarter microseconds, with a range from 3000-9000
    return 3000+int((90.0 + (deg/180.0))*6000)

Protocol = pyflightcontrol.system.RpcProtocol('actuate',
        pyflightcontrol.ports.tcpPort('actuate'),
        pyflightcontrol.proto.actuation_query,
        pyflightcontrol.proto.actuation_response)

class Server(pyflightcontrol.system.RpcServer):
    def __init__(self):
        self.aileron = 0.0
        self.elevator = 0.0
        self.rudder = 0.0
        self.motor = 0.0
        self.lock = threading.Lock()
        self.ctrl = Maestro.createMicro()
        self._doSet()
        protocol = Protocol
        protocol.addAction('setvals', self.handleSetvals)
        protocol.addAction('getvals', self.handleGetvals)
        super().__init__(protocol)

    def _doSet(self):
        with self.lock:
            self.ctrl.setTarget(ports.servo['aileron_r'], getPWM(self.aileron))
            self.ctrl.setTarget(ports.servo['aileron_l'], getPWM(-self.aileron))
            self.ctrl.setTarget(ports.servo['elevator'], getPWM(self.elevator))
            self.ctrl.setTarget(ports.servo['rudder'], getPWM(self.rudder))

    def handleSetvals(self, actuation_vars, timestamp):
        pkt = pyflightcontrol.proto.bool_wrap()
        pkt.value = True
        with self.lock:
            self.aileron = actuation_vars.d_a
            self.elevator = actuation_vars.d_e
            self.rudder = actuation_vars.d_r
            self.motor = actuation_vars.motor_pwr
        self._doSet()
        return pkt

    def handleGetvals(self, flag, timestamp):
        pkt = pyflightcontrol.proto.actuation_vars()
        with self.lock:
            pkt.d_a = self.aileron
            pkt.d_e = self.elevator
            pkt.d_r = self.rudder
            pkt.motor_pwr = self.motor
        return pkt

class Client(pyflightcontrol.system.RpcClient):
    def __init__(self, log):
        super().__init__(pyflightcontrol.ports.tcpHost('actuate'), 
                DAQProtocol, log)

    def getvals(self):
        pkt = pyflightcontrol.proto.bool_wrap()
        pkt.value = True;
        ret = self.query('getvals', pkt)
        return ret

    def setvals(self, d_a, d_e, d_r, motor_pwr):
        pkt = pyflightcontrol.proto.actuation_vars()
        pkt.d_a = d_a
        pkt.d_e = d_e
        pkt.d_r = d_r
        pkt.motor_pwr = motor_pwr
        ret = self.query('setvals', pkt)
        if ret is None:
            return False
        return True

if __name__ == '__main__':
    srv = Server()
    srv.startDaemon()
