from . import ports
from . import math
import serial
import struct

class IMU(object):
    def __init__(self, tty):
        self._dev = serial.Serial(tty, 57600)
        self._dev.write('#oqb')
        self._dev.write('#sxy')
        key = '#SYNCxy'
        buf = ''.join(chr((ord(c) + 1)  & 0xFF) for c in key)
        while buf != key:
            buf = buf[1:] + self._dev.read(1)
        self.attitude = math.Quaternion(0, 1, 0, 0)
        self.accel = [0, 0, 1]
        self.gyro = [0, 0, 0]
        self.mag = [0, 0, 0]

    def tryUpdate(self):
        if self._dev.read.in_waiting > 0:
            data = self._dev.read(4*4)
            self.attitude.do_set(*struct.unpack('<ffff', data))
            data = self._dev.read(3*4)
            self.accel = list(struct.unpack('<fff'), data)
            data = self._dev.read(3*4)
            self.mag = list(struct.unpack('<fff'), data)
            data = self._dev.read(3*4)
            self.gyro = list(struct.unpack('<fff'), data)
            return True
        return False
    
    @classmethod
    def create(cls):
        return cls(ports.imu_dev)

if __name__ == '__main__':
    from time import sleep
    imu = IMU.create()
    while True:
        if imu.tryUpdate():
            attitude = imu.attitude.euler()
            print('Pitch {}\tRoll {}\tYaw {}\n'.format(attitude.pitch, 
                    attitude.roll, attitude.yaw))
            print('Accel {}\t{}\t{}\n'.format(*imu.accel))
            print('Gyro {}\t{}\t{}\n'.format(*imu.gyro))
            print('Mag {}\t{}\t{}\n'.format(*imu.mag))
        sleep(0.005)
