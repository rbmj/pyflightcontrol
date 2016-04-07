from . import actuate
import logging

if __name__ == '__main__':
    d_a = 0.0
    d_e = 0.0
    d_r = 0.0
    motor = 0.0
    client = actuate.Client(logging)
    while True:
        line = input('> ').split()
        cmd = line[0]
        if cmd == 'exit':
            break
        if cmd == 'get':
            pkt = client.getvals()[0]
            print('{:2.3f}:{:2.3f}:{:2.3f}:{:2.3f}'.format(
                pkt.d_a, pkt.d_e, pkt.d_r, pkt.motor_pwr))
        if len(line) != 2:
            continue
        arg = float(line[1])
        if cmd == 'aileron':
            d_a = arg
        elif cmd == 'rudder':
            d_r = arg
        elif cmd == 'elevator':
            d_e = arg
        elif cmd == 'motor':
            motor = arg
        client.setvals(d_a, d_e, d_r, motor)
