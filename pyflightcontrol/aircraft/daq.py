from SelectServer import SelectServer
from usb import core
import threading
import serial
import ports
import time

from .bme280 import BME280

imu_dev = (0xfeed, 0xface) # Vendor/Product ID of USB device
imu_usb = core.find(idVendor=imu_dev[0], idProduct=imu_dev[1])
imu_fname = '/dev/bus/usb/{:03}/{:03}'.format(imu_usb.bus, imu_usb.address)
imu_serial = serial.Serial(
        port=imu_fname,
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
)

# Pressure
P = 2117
T = 460+50

# Attitude Quaternion
e0 = 0
ex = 1
ey = 0
ez = 0

# Load Factors
nx = 0
ny = 0
nz = 1

# Gyro
p = 0
q = 0
r = 0

def getIMU():
    pass

def getAtmos():
    pass

def getPitot():
    pass

dataLock = threading.Lock()

def doDAQ():
    while True:
        dataLock.acquire()
        getIMU()
        getAtmos()
        #getPitot()
        dataLock.release()
        time.sleep(0.025)

daqThread = threading.Thread(doDAQ)

def handleRequest(srv, sock):
    pass

srv = SelectServer(ports.tcpPort(ports.tcp['daq']), handleRequest)

while True:
    srv.run()
