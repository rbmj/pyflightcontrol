from smbus import SMBus
from sys import exit
import os
import time

class MPL3115A2(object):

    #I2C ADDRESS/BITS
    ADDRESS = (0x60)
    
    #REGISTERS
    REGISTER_STATUS = (0x00)
    REGISTER_STATUS_TDR = 0x02
    REGISTER_STATUS_PDR = 0x04
    REGISTER_STATUS_PTDR = 0x08

    REGISTER_PRESSURE_MSB = (0x01)
    REGISTER_PRESSURE_CSB = (0x02)
    REGISTER_PRESSURE_LSB = (0x03)

    REGISTER_TEMP_MSB = (0x04)
    REGISTER_TEMP_LSB = (0x05)

    REGISTER_DR_STATUS = (0x06)

    OUT_P_DELTA_MSB = (0x07)
    OUT_P_DELTA_CSB = (0x08)
    OUT_P_DELTA_LSB = (0x09)

    OUT_T_DELTA_MSB = (0x0A)
    OUT_T_DELTA_LSB = (0x0B)

    BAR_IN_MSB = (0x14)

    WHOAMI = (0x0C)

    #BITS
    PT_DATA_CFG = 0x13
    PT_DATA_CFG_TDEFE = 0x01
    PT_DATA_CFG_PDEFE = 0x02
    PT_DATA_CFG_DREM = 0x04

    CTRL_REG1 = (0x26)
    CTRL_REG1_SBYB = 0x01
    CTRL_REG1_OST = 0x02
    CTRL_REG1_RST = 0x04
    CTRL_REG1_OS1 = 0x00
    CTRL_REG1_OS2 = 0x08
    CTRL_REG1_OS4 = 0x10
    CTRL_REG1_OS8 = 0x18
    CTRL_REG1_OS16 = 0x20
    CTRL_REG1_OS32 = 0x28
    CTRL_REG1_OS64 = 0x30
    CTRL_REG1_OS128 = 0x38
    CTRL_REG1_RAW = 0x40
    CTRL_REG1_ALT = 0x80
    CTRL_REG1_BAR = 0x00
    CTRL_REG2 = (0x27)
    CTRL_REG3 = (0x28)
    CTRL_REG4 = (0x29)
    CTRL_REG5 = (0x2A)

    REGISTER_STARTCONVERSION = (0x12)

    def __init__(self):
        os.system('echo -n 1 > ' +
                '/sys/module/i2c_bcm2708/parameters/combined')
        self._bus = SMBus(1)
        whoami = self._bus.read_byte_data(MPL3115A2.ADDRESS, 
                MPL3115A2.WHOAMI)
        if whoami != 0xc4:
            raise #FIXME

        # Enable Event Flags
        self._bus.write_byte_data(MPL3115A2.ADDRESS,
                MPL3115A2.PT_DATA_CFG, 0x07) 
        
        self.pressure = 0
        self.temperature = 0

    def poll(self):
        self._bus.read_byte_data(MPL3115A2.ADDRESS, MPL3115A2.CTRL_REG1)
        self._bus.write_byte_data(
                MPL3115A2.ADDRESS,
                MPL3115A2.CTRL_REG1, 
                MPL3115A2.CTRL_REG1_OST |
                MPL3115A2.CTRL_REG1_OS8)
        while True:
            reg = self._bus.read_byte_data(MPL3115A2.ADDRESS,
                    MPL3115A2.REGISTER_STATUS)
            if (reg & MPL3115A2.REGISTER_STATUS_PTDR) != 0:
                break
        msb, csb, lsb = self._bus.read_i2c_block_data(MPL3115A2.ADDRESS,
                MPL3115A2.REGISTER_PRESSURE_MSB, 3)
        self.pressure = ((msb<<16) | (csb<<8) | lsb) / 64.
        # convert to psf
        self.pressure = self.pressure*0.02089
        msb, lsb = self._bus.read_i2c_block_data(MPL3115A2.ADDRESS,
                MPL3115A2.REGISTER_TEMP_MSB, 2)
        self.temperature = (msb << 8) | lsb
        # check sign
        if self.temperature > (1<<15):
            self.temperature = self.temperature - (1<<16)
        # make fractional and convert to kelvin
        self.temperature = (self.temperature/256.) + 273.15
        # convert to rankine
        self.temperature = self.temperature*1.8

if __name__ == '__main__':
    dev = MPL3115A2()
    while True:
        dev.poll()
        print('p {}\tT {}'.format(dev.pressure, dev.temperature))
        time.sleep(0.05)
