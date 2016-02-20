from SelectServer import SelectServer
from usb import core
from maestro import Controller
import threading
import ports
import proto.dolos_pb2
import utils

# Get Servo Multiplexer Device File
# This could be done less cruftily
snum = core.find(idVendor=0x1ffb, idProduct=0x0089).serial_number
prod = 'Pololu_Corporation_Pololu_Micro_Maestro_6-Servo_Controller'
# if00 is generally the command port, with if02 the control port
dev = '/dev/serial/by-id/usb-{}_{}-if00'.format(prod, snum)

def getPWM(deg):
    # units are in quarter microseconds, with a range from 3000-9000
    return 3000+int((90.0 + (deg/180.0))*6000)

class State(object):
    def __init__(self):
        self.aileron = 0.0
        self.elevator = 0.0
        self.rudder = 0.0
        self.motor = 0.0
        self.lock = threading.Lock()
        self.ctrl = Controller(dev)
        self._doSet()

    def get(self):
        with self.lock:
            return (self.aileron, self.elevator, self.rudder, self.motor)

    def setvars(self, a, e, r, m):
        with self.lock:
            self.aileron = a
            self.elecator = e
            self.rudder = r
            self.motor = m
        self._doSet()

    def _doSet(self):
        with self.lock:
            self.ctrl.setTarget(ports.servo['aileron_r'], getPWM(self.aileron))
            self.ctrl.setTarget(ports.servo['aileron_l'], getPWM(-self.aileron))
            self.ctrl.setTarget(ports.servo['elevator'], getPWM(self.elevator))
            self.ctrl.setTarget(ports.servo['rudder'], getPWM(self.rudder))

state = State()

def handleRequest(srv, sock):
    try:
        acstate = dolos_pb2.actuation_vars()
        if utils.readBuffer(acstate, sock) is None:
            srv.closeConnection(srv, sock)
            return
        state.setvars(acstate.d_a, acstate.d_e, acstate.d_r, acstate.motor_pwr)
    except:
        srv.closeConnection(srv, sock)

def handlePollRequest(srv, sock):
    try:
        msg = sock.recv(2)
        if msg[0] == 0xFF and msg[1] == 0xFF:
            srv.closeConnection(srv, sock)
            return
        acstate = dolos_pb2.actuation_vars()
        (a, e, r, m) = state.get()
        acstate.d_a = a
        acstate.d_e = e
        acstate.d_r = r
        acstate.motor_pwr = m
        utils.sendBuffer(acstate, sock)
    except:
        srv.closeConnection(srv, sock)

srv = SelectServer(ports.tcpPort(ports.tcp['actuate']), handleRequest)
srvpoll = SelectServer(ports.tcpPort(ports.tcp['actuate_poll']), handlePollRequest)

def runServer(arg):
    while True:
        arg.run()

pollthread = threading.Thread(target=runServer, args=(srvpoll,))
pollthread.start()
runServer(srv)
