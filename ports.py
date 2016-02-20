
# TCP hosts/ports
tcp = {
    'daq': '127.0.0.1:16000',
    'filter': '127.0.0.1:16001',
    'actuate': '127.0.0.1:16002',
    'c3': '127.0.0.1:16003',
    'jamming': '127.0.0.1:16004',
    'control': '127.0.0.1:16005',
    'actuate_poll': '127.0.0.1:16006'
}

def tcpPort(name):
    return int(tcp[name].split(':')[1])

def tcpHost(name):
    return tcp[name].split(':')[0]

# Maestro Servo Channels
servo = {
    'rudder': 0,
    'elevator': 1,
    'aileron_l': 2,
    'aileron_r': 3
}


