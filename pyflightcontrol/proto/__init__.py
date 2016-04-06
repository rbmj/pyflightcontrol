from google.protobuf.timestamp_pb2 import Timestamp
import time

def stamp():
    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 1e9)
    return Timestamp(seconds=seconds, nanos=nanos)

def gettm(tm):
    return tm.seconds + tm.nanos*1e-9

from .pyflightcontrol_pb2 import *
