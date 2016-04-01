import math
import numpy

class Euler(object):
    def __init__(self, roll, pitch, bear):
        self._vec = numpy.array([roll, pitch, bear])

    @property
    def roll(self):
        return self._vec[0]

    @property
    def roll_d(self):
        return self.roll*180/math.pi

    @property
    def pitch(self):
        return self._vec[1]

    @property
    def pitch_d(self):
        return self.pitch*180/math.pi

    @property
    def bearing(self):
        return self._vec[2]

    @property
    def bearing_d(self):
        b = self.bearing*180/math.pi
        if b < 0:
            return b + 180
        return b

    @property
    def vec(self):
        return self._vec

    def quaternion(self):
        c = math.cos
        s = math.sin
        v = self._vec / 2
        return Quaternion(
                c(v[0])*c(v[1])*c(v[2]) + s(v[0])*s(v[1])*s(v[2]),
                s(v[0])*c(v[1])*c(v[2]) + c(v[0])*s(v[1])*s(v[2]),
                c(v[0])*s(v[1])*c(v[2]) + s(v[0])*c(v[1])*s(v[2]),
                c(v[0])*c(v[1])*s(v[2]) + s(v[0])*s(v[1])*c(v[2]))


class Quaternion(object):
    def __init__(self, e0, ex, ey, ez):
        self._quat = numpy.array([e0, ex, ey, ez])

    def __mul__(self, q):
        return Quaternion(
                self.e0*q.e0 - self.ex*q.ex - self.ey*q.ey - self.ez*q.ez,
                self.e0*q.ex + self.ex*q.e0 + self.ey*q.ez - self.ez*q.ey,
                self.e0*q.ey - self.ex*q.ez + self.ey*q.e0 + self.ez*q.ex,
                self.e0*q.ez + self.ex*q.ey - self.ey*q.ex + self.ez*q.e0)
    @property
    def ex(self):
        return self._quat[1]

    @property
    def ey(self):
        return self._quat[2]

    @property
    def ez(self):
        return self._quat[3]

    @property
    def e0(self):
        return self._quat[0]

    def do_set(self, e0, ex, ey, ez):
        self._quat = numpy.array([e0, ex, ey, ez])

    @property
    def conj(self):
        return Quaternion(self.e0, -self.ex, -self.ey, -self.ez)

    @staticmethod
    def square(quat):
        return Quaternion(quat.e0*quat.e0,
                          quat.ex*quat.ex,
                          quat.ey*quat.ey,
                          quat.ez*quat.ez)
    
    def normalize(self):
        self._quat = self._quat/numpy.linalg.norm(self._quat)

    def euler(self):
        q = Quaternion.square(self)
        roll = math.atan2(2*(self.e0*self.ex + self.ey*self.ez),
                q.e0 + q.ez - q.ex - q.ey)
        pitch = math.asin(2*(self.e0*self.ey - self.ex*self.ez))
        bear = math.atan2(2*(self.e0*self.ez + self.ex*self.ey),
                q.e0 + q.ex - q.ey - q.ez)
        return Euler(roll, pitch, bear)

