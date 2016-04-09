import pyflightcontrol
import math

# Density Ratio every 1000 ft starting at 0
sigma_tab = [
        1.0000, 0.9711, 0.9428, 0.9151, 0.8881, 0.8617, 0.8359, 0.8107,
        0.7861, 0.7621, 0.7386, 0.7157, 0.6933, 0.6715, 0.6502, 0.6295,
        0.6092, 0.5895, 0.5702, 0.5514, 0.5332, 0.5153, 0.4980, 0.4811,
        0.4646, 0.4486, 0.4330, 0.4178, 0.4031, 0.3887, 0.3747, 0.3611,
        0.3480, 0.3351, 0.3227, 0.3106, 0.2988, 0.2852, 0.2719, 0.2592,
        0.2471, 0.2355, 0.2245, 0.2140, 0.2040, 0.1945, 0.1854, 0.1767,
        0.1685, 0.1606, 0.1531, 0.1460, 0.1391, 0.1326, 0.1264, 0.1205,
        0.1149, 0.1096, 0.1044, 0.0996, 0.0949, 0.0905, 0.0863, 0.0822,
        0.0784, 0.0747]

# Pressure Ratio every 1000 ft starting at 0
delta_tab = [
        1.0000, 0.9644, 0.9298, 0.8963, 0.8637, 0.8321, 0.8014, 0.7717,
        0.7429, 0.7149, 0.6878, 0.6616, 0.6362, 0.6115, 0.5877, 0.5646,
        0.5422, 0.5206, 0.4997, 0.4795, 0.4599, 0.4410, 0.4227, 0.4051,
        0.3880, 0.3716, 0.3557, 0.3404, 0.3256, 0.3113, 0.2975, 0.2843,
        0.2715, 0.2592, 0.2474, 0.2360, 0.2250, 0.2145, 0.2044, 0.1949,
        0.1858, 0.1771, 0.1688, 0.1609, 0.1534, 0.1462, 0.1394, 0.1329,
        0.1267, 0.1208, 0.1151, 0.1097, 0.1046, 0.0997, 0.0951, 0.0906,
        0.0864, 0.0824, 0.0785, 0.0749, 0.0714, 0.0680, 0.0649, 0.0618,
        0.0590, 0.0562]

def interpolate_altitude(tab, reading):
    interp_pos = 0
    if reading > tab[0]:
        pass
    elif reading < tab[-1]:
        interp_pos = len(tab)-2
    else:
        while reading < tab[interp_pos]:
            interp_pos = interp_pos + 1
        interp_pos = interp_pos - 1
    return interp_pos*1000+(1000*(reading - tab[interp_pos])
            /(tab[interp_pos+1] - tab[interp_pos]))

def reverse_interp(tab, alt):
    interp_pos = 0
    if alt < 0:
        pass
    elif alt >= (len(tab)-1)*1000:
        interp_pos = len(tab)-2
    else:
        interp_pos = int(alt // 1000)
    dh = alt/1000 - interp_pos
    return tab[interp_pos] + dh*(tab[interp_pos+1]-tab[interp_pos])


class AircraftState(object):
    
    R = 1716 # ft-lb/slug-R
    qnhconv = 1.414 # psf to hundredths of mercury
    rhoSSL = 0.0023769 # slugs/ft^3
    TSSL = 518.7
    pSSL = 2116.9

    def __init__(self, qnh = 2992):
        self.airspeed = 0
        self._attitude = pyflightcontrol.angle.Quaternion(1, 0, 0, 0)
        self.load = [0, 0, 1] # [nx, ny, nz]
        self.rates = [0, 0, 0] # [p, q, r]
        self.location_offset = [0, 0]
        self.p = AircraftState.pSSL # psf
        self.T = AircraftState.TSSL # deg R
        self._qnh = qnh/AircraftState.qnhconv
        self._euler = self._attitude.euler()
        self.v = 0
        self.rudder = 0
        self.aileron = 0
        self.elevator = 0
        self.motor = 0

    #FIXME
    @classmethod
    def unserialize(cls, pkt):
        this = cls()
        if pkt.HasField('load'):
            this.load = [pkt.load.nx, pkt.load.ny, pkt.load.nz]
        if pkt.HasField('quat'):
            this._attitude = pyflightcontrol.angle.Quaternion(
                    pkt.quat.e0, pkt.quat.ex, pkt.quat.ey, pkt.quat.ez)
            this._euler = this.load.euler()
        if pkt.HasField('v_inf'):
            this.v = pkt.v_inf
        if pkt.HasField('p'):
            this.p = pkt.p
        elif pkt.HasField('h'):
            this.p = AircraftState.pSSL*reverse_interp(delta_tab, pkt.h)
        if pkt.HasField('T'):
            this.T = pkt.T
        if pkt.HasField('x') and pkt.HasField('y'):
            this.location_offset = [pkt.x, pkt.y]
        if pkt.HasField('qnh'):
            this._qnh = pkt.qnh
        return this

    def serialize(self, pkt):
        pkt.load.nx = self.load[0]
        pkt.load.ny = self.load[1]
        pkt.load.nz = self.load[2]
        pkt.quat.e0 = self._attitude.e0
        pkt.quat.ex = self._attitude.ex
        pkt.quat.ey = self._attitude.ey
        pkt.quat.ez = self._attitude.ez
        pkt.rates.p = self.rates[0]
        pkt.rates.q = self.rates[1]
        pkt.rates.r = self.rates[2]
        pkt.v_inf = self.v
        pkt.h = self.pressure_altitude
        pkt.x = self.location_offset[0]
        pkt.y = self.location_offset[1]
        pkt.T = self.T
        pkt.p = self.p
        pkt.qnh = self._qnh

    @property
    def oat(self):
        return self.T - 460
    
    @property
    def qnh(self):
        return int(round(AircraftState.qnhconv*self._qnh))

    @qnh.setter
    def qnh(self, val):
        self._qnh = val/AircraftState.qnhconv
    
    @property
    def quaternion(self):
        return self._attitude

    @quaternion.setter
    def quaternion(self, val):
        self._attitude = val
        self._euler = val.euler()

    @property
    def euler(self):
        return self._euler

    @euler.setter
    def euler(self, val):
        self._euler = val
        self._attitude = val.quaternion()

    @property
    def pressure_altitude(self):
        return interpolate_altitude(delta_tab, self.p/self._qnh)

    @property
    def rho(self):
        return p/(AircraftState.R*T)

    @property
    def density_altitude(self):
        return interpolate_altitude(sigma_tab, self.rho/AircraftState.rhoSSL)

    @property
    def pitch(self):
        return self._euler.pitch_d

    @property
    def roll(self):
        return self._euler.roll_d

    @property
    def bearing(self):
        return self._euler.bearing_d
