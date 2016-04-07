from usb import core
from google.protobuf.message import DecodeError
import serial
import struct
import enum

class XBee(object):

    MAGIC = struct.pack('!I', 0xd0105acf)
    BUFINIT = 'AAAA'.encode('ascii')

    class State(enum.Enum):
        SYNC = 1
        GETLEN = 2
        READ = 3
    
    @staticmethod
    def findExplorerDev():
        # Get XBee Device File - for SparkFun XBee Explorer
        # This could be done less cruftily
        desc = core.find(idVendor=0x0403, idProduct=0x6015)
        if desc is None:
            return None
        snum = desc.serial_number
        prod = 'FTDI_FT231X_USB_UART'
        dev = '/dev/serial/by-id/usb-{}_{}-if00-port0'.format(prod, snum)
        return dev

    @staticmethod
    def findRPiSerialDev():
        return '/dev/ttyAMA0'
    
    def __init__(self, dev):
        self._dev = serial.Serial(dev, 57600)
        self._state = XBee.State.SYNC
        self._buf = XBee.BUFINIT
        self._pktlen = 0

    def serialReadBuffer(self, protobuf):
        buf = XBee.BUFINIT
        while buf != XBee.MAGIC:
            buf = buf[1:] + self._dev.read(1)
        l = struct.unpack('!H', self._dev.read(2))[0]
        buf = self._dev.read(l)
        pkt = protobuf()
        try:
            pkt.ParseFromString(buf)
        except DecodeError:
            pkt = None #FIXME: silently drop
        # Need to resynchronize now that we've messed with things
        self._state = XBee.State.SYNC
        self._buf = XBee.BUFINIT
        return pkt
    
    def readPktAsync(self, protobuf, cb):
        try:
            if self._state == XBee.State.SYNC:
                while self._dev.inWaiting() > 0:
                    if self._buf == XBee.MAGIC:
                        self._buf = b''
                        self._state = XBee.State.GETLEN
                        break
                    self._buf = self._buf[1:] + self._dev.read(1)
            if self._state == XBee.State.GETLEN:
                while self._dev.inWaiting() > 0:
                    if len(self._buf) == 2:
                        self._pktlen = struct.unpack('!H', self._buf)[0]
                        self._state = XBee.State.READ
                        self._buf = b''
                        break
                    self._buf = self._buf + self._dev.read(1)
            if self._state == XBee.State.READ:
                remLen = self._pktlen - len(self._buf)
                readLen = min(remLen, self._dev.inWaiting())
                self._buf = self._buf + self._dev.read(readLen)
                if len(self._buf) == self._pktlen:
                    pkt = protobuf()
                    try:
                        pkt.ParseFromString(self._buf)
                    except DecodeError:
                        pass #FIXME: silently drop
                    else:
                        cb(pkt)
                    self._state = XBee.State.SYNC
                    self._buf = XBee.BUFINIT
        except:
            # if there's an error, try and resynchronize
            self._state = XBee.State.SYNC
            self._buf = XBee.BUFINIT
            raise

    def writePkt(self, pkt):
        msg = pkt.SerializeToString()
        self._dev.write(XBee.MAGIC + struct.pack('!H', len(msg)) + msg)

if __name__ == '__main__':
    from . import proto
    from time import sleep
    from datetime import datetime
    def handle(pkt):
        print('Received timestamp ' + 
                str(datetime.fromtimestamp(proto.gettm(pkt))))
    dev = XBee.findExplorerDev()
    if dev is None:
        dev = XBee.findRPiSerialDev()
    xbee = XBee(dev)
    while True:
        pkt = proto.stamp()
        print('sending timestamp')
        xbee.writePkt(pkt)
        pkt = xbee.readPktAsync(proto.Timestamp, handle)
        sleep(1)

