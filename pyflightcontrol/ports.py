# Maestro Servo Channels
servo = {
    'rudder': 0,
    'elevator': 1,
    'aileron_l': 2,
    'aileron_r': 3
}

# Serial Device SNs:
imu_sn = 'AI041T93'
gps_sn = 'XXXXXXXX' #FIXME

# TCP hosts/ports
tcp = {
    'daq': '127.0.0.1:16000',
    'filter': '127.0.0.1:16001',
    'actuate': '127.0.0.1:16002',
    'c3': '127.0.0.1:16003',
    'jamming': '127.0.0.1:16004',
    'control': '127.0.0.1:16005',
}

# device names:
imu_dev_name = 'usb-FTDI_FT232R_USB_UART_{}-if00-port0'.format(imu_sn)
imu_dev = '/dev/serial/by-id/' + imu_dev_name

gps_dev_name = 'usb-FTDI_FT232R_USB_UART_{}-if00-port0'.format(gps_sn)
gps_dev = '/dev/serial/by-id/' + gps_dev_name

def tcpPort(name):
    return int(tcp[name].split(':')[1])

def tcpHost(name):
    return tcp[name].split(':')[0]

def tcpTuple(name):
    x = tcp[name].split(':')
    return (x[0], int(x[1]))

