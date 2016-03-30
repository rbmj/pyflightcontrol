from SelectServer import SelectServer
from usb import core
import threading
import serial
import ports

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

dataLock = threading.Lock()

def doDAQ():
    while True:
        dataLock.acquire()
        getIMU()
        getAtmos()
        #getPitot()
        dataLock.release()
        

daqThread = threading.Thread(doDAQ)

def handleRequest(srv, sock):
    pass

srv = SelectServer(ports.tcpPort(ports.tcp['daq']), handleRequest)

while True:
    srv.run()
