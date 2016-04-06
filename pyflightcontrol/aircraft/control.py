import pyflightcontrol
import daemon
from daemon.pidfile import PIDLockFile
import logging
import time
import signal

class Server(object):
    def __init__(self):
        self._context = daemon.DaemonContext(
                working_directory='/var/lib',
                umask=0o002,
                pidfile=PIDLockFile('/var/run/pfc-control.pid'),
                detach_process=True
        )
        self._context.signal_map = {
            signal.SIGTERM:  'terminate'
        }
        #context.gid = grp.getgrnam('foo').gr_gid
        self._context.files_preserve = []
        self._log = logging

    def _post_init(self):
        self.xbee = pyflightcontrol.XBee(pyflightcontrol.XBee.findRPiSerialDev())
        self.daq = pyflightcontrol.aircraft.daq.Client(self._log)
        self.actuate = pyflightcontrol.aircraft.actuate.Client(self._log)
        self._last_update = None
        self._sensor_vals = None
        self._actuate_vals = None

    def handleUplink(self, pkt):
        self._last_update = pyflightcontrol.proto.Timestamp()
        self._last_update.MergeFrom(pkt.time)
        pkt_type = pkt.WhichOneof('uplink_type')
        print('received uplink packet type ' + pkt_type)
        if pkt_type == 'manual':
            self.actuate.setvals(pkt.manual.d_a, pkt.manual.d_e,
                    pkt.manual.d_r, pkt.manual.motor_pwr)

    def event_loop(self, send_telemetry):
        self.xbee.readPktAsync(pyflightcontrol.proto.command_uplink, self.handleUplink)
        self._sensor_vals = self.daq.measure()
        self._actuate_vals = self.actuate.getvals()
        if send_telemetry:
            pkt = pyflightcontrol.proto.command_downlink()
            if not (self._last_update is None):
                pkt.last_update.MergeFrom(self._last_update)
            if not (self._sensor_vals is None):
                pkt.manual.sensors.MergeFrom(self._sensor_vals[0])
            if not (self._actuate_vals is None):
                pkt.manual.actuation.MergeFrom(self._actuate_vals[0])
            pkt.time.MergeFrom(pyflightcontrol.proto.stamp())
            self.xbee.writePkt(pkt)

    def main(self):
        sendpkt_freq = 2 # once every N packets
        loop_period = 1/20. # 20 Hz
        counter = 0
        while True:
            end_time = time.time() + loop_period
            try:
                self.event_loop(counter == 0)
            except Exception as e:
                self._log.exception(e)
            counter = (counter + 1) % sendpkt_freq
            try:
                time.sleep(end_time - time.time())
            except ValueError:
                self._log.warning('Event Loop SLOW')

    def startDaemon(self):
        try:
            with self._context:
                self._log = logging.getLogger('pfc-control')
                loghnd = logging.handlers.SysLogHandler(address='/dev/log')
                self._log.addHandler(loghnd)
                self._post_init()
                self.main()
        except Exception as e:
            self._log.exception(e)

    def start(self):
        try:
            self._post_init()
            self.main()
        except Exception as e:
            self._log.exception(e)

if __name__ == '__main__':
    srv = Server()
    srv.start()
