from . import daq
from ..angle import Quaternion, Euler
import logging

if __name__ == '__main__':
    client = daq.Client(logging)
    while True:
        line = input('> ')
        if line == 'exit':
            break
        if line == 'measure':
            print('Taking measurement...')
            vals = client.measure()
            if vals is None:
                print('ERROR')
                continue
            vals = vals[0]
            att = Quaternion(vals.ahrs.e0, vals.ahrs.ex, vals.ahrs.ey,
                    vals.ahrs.ez)
            eul = att.euler()
            print('{:2.1f}:{:2.1f}:{:2.1f} p/r/y'.format(eul.pitch_d,
                    eul.roll_d, eul.bearing_d))
            print('{:2.1f} psf/{:2.1f} F'
                    .format(vals.static, vals.temp-460))

