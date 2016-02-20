from usb import core
from maestro import Controller

# Get Servo Multiplexer Device File
# This could be done less cruftily
snum = core.find(idVendor=0x1ffb, idProduct=0x0089).serial_number
prod = 'Pololu_Corporation_Pololu_Micro_Maestro_6-Servo_Controller'
# if00 is generally the command port, with if02 the control port
dev = '/dev/serial/by-id/usb-{}_{}-if00'.format(prod, snum)

ctrl = Controller(dev)

