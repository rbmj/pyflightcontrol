import pyflightcontrol
import math
import serial
import struct
import time

quat = pyflightcontrol.angle.Quaternion
DEBUG_QUAT = True
IMU_ORIENT = quat(0, 1, 0, 0)

class IMU(object):
    def __init__(self, tty):
        self._dev = serial.Serial(tty, 57600)
        # The sleep and multiple output format specifiers seem necessary
        # for some reason - maybe a lag time in the serial clocks getting
        # synched
        time.sleep(0.3)
        self._dev.write(b'#oqb')
        self._dev.write(b'#oqb')
        self._dev.write(b'#oqb')
        self._dev.write(b'#oqb')
        self._dev.write(b'#oqb')
        self.sync()
        self.attitude = quat(0, 1, 0, 0)
        self.accel = [0, 0, 1]
        self.gyro = [0, 0, 0]
        self.mag = [0, 0, 0]
        self.mode = 0

    def sync(self):
        self._dev.write(b'#sxy')
        key = b'#SYNCHxy\r\n'
        buf = b'A'*len(key)
        while buf != key:
            buf = buf[1:] + self._dev.read(1) 

    def tryUpdate(self):
        if self._dev.inWaiting() > 0:
            self.update()
            return True
        return False

    def update(self):
        if DEBUG_QUAT:
            self.mode = ord(self._dev.read(1))+1
        data = self._dev.read(4*4)
        self.attitude.do_set(*struct.unpack('<ffff', data))
        data = self._dev.read(3*4)
        self.accel = list(struct.unpack('<fff', data))
        data = self._dev.read(3*4)
        self.mag = list(struct.unpack('<fff', data))
        data = self._dev.read(3*4)
        self.gyro = list(struct.unpack('<fff', data))
        self._reorient()

    def _reorient(self):
        self.attitude = self.attitude.rotateBy(IMU_ORIENT)
        self.accel = quat.fromVec(self.accel).rotateBy(IMU_ORIENT).vector
        self.gyro = quat.fromVec(self.gyro).rotateBy(IMU_ORIENT).vector
        self.mag = quat.fromVec(self.mag).rotateBy(IMU_ORIENT).vector
 
    @classmethod
    def create(cls):
        return cls(pyflightcontrol.ports.imu_dev)

if __name__ == '__main__':
    imu = IMU.create()
    while True:
        if imu.tryUpdate():
            attitude = imu.attitude.euler()
            pitch = 180/math.pi * attitude.pitch
            roll = 180/math.pi * attitude.roll
            yaw = 180/math.pi * attitude.bearing
            print('{}Pitch {:2.3f}\tRoll {:2.3f}\tYaw {:2.3f}'.format(
                    imu.mode, pitch, roll, yaw))
            #print('Accel {:2.3f}\t{:2.3f}\t{:2.3f}'.format(*imu.accel))
            #print('Gyro {:2.3f}\t{:2.3f}\t{:2.3f}'.format(*imu.gyro))
            #print('Mag {:2.3f}\t{:2.3f}\t{:2.3f}'.format(*imu.mag))
        time.sleep(0.005)
