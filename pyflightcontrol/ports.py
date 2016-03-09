
# TCP hosts/ports
tcp = {
    'daq': '127.0.0.1:16000',
    'filter': '127.0.0.1:16001',
    'actuate': '127.0.0.1:16002',
    'c3': '127.0.0.1:16003',
    'jamming': '127.0.0.1:16004',
    'control': '127.0.0.1:16005',
}

def tcpPort(name):
    return int(tcp[name].split(':')[1])

def tcpHost(name):
    return tcp[name].split(':')[0]

def tcpTuple(name):
    x = tcp[name].split(':')
    return (x[0], int(x[1]))

# Maestro Servo Channels
servo = {
    'rudder': 0,
    'elevator': 1,
    'aileron_l': 2,
    'aileron_r': 3
}


