import asyncio, evdev, time

class Joystick(object):
    from evdev import ecodes
    def __init__(self, dev):
        if isinstance(dev, str):
            self._dev = evdev.InputDevice(dev)
        else:
            self._dev = dev
        self._axes = {}
        self._buttons = {}
        self._handlers = {}

    @asyncio.coroutine
    def _pump(self):
        while True:
            events = yield from self._dev.async_read()
            for event in events:
                if event.type == ecodes.EV_ABS:
                    self._axes[event.code] = event.value
                elif event.type == evdev.EV_KEY:
                    self._buttons[event.code] = event.value
                    h = self._handlers.get(event.value)
                    if h:
                        h()

    def register(self):
        asyncio.async(self._pump())

    def addButtonHandler(self, h, code):
        self._handlers[code] = h

    def getX(self):
        return self._axes[ecodes.ABS_X]

    def getY(self):
        return self._axes[ecodes.ABS_Y]

    def getZ(self):
        return self._axes[ecodes.ABS_Z]

    def getAxis(self, code):
        return self._axes[code]

    def getButton(self, code):
        return self._buttons[code]
    
    def enumerateButtons(self, resolve=True):
        cap = self._dev.capabilities(verbose=False, absinfo=False)
        btns = cap[ecodes.EV_KEY]
        if resolve:
            names = [name if isinstance(name, str) else name[-1]
                        for name in (ecodes.BTN[x] for x in btns)]
            return [x for x in zip(names, btns)]
        return btns

    def enumerateAxes(self, resolve=True):
        cap = self._dev.capabilities(verbose=False, absinfo=False)
        axes = cap[ecodes.EV_ABS]
        if resolve:
            names = [ecodes.ABS[x] for x in axes]
            return [x for x in zip(names, axes)]
        return axes

    @staticmethod
    def autodetect():
        out = {}
        devs = [evdev.InputDevice(d) for d in evdev.util.list_devices()]
        caps = [d.capabilities(verbose=False, absinfo=False) for d in devs]
        btns = [len(c.get(evdev.ecodes.EV_KEY, [])) for c in caps]
        axes = [len(c.get(evdev.ecodes.EV_ABS, [])) for c in caps]
        data = [x for x in zip(devs, caps, btns, axes)]
        sticks = filter(lambda x: x[3] >= 3 and x[2] > 1, data)
        out['stick'] = [Joystick(x[0]) for x in sticks]
        rudders = filter(lambda x: x[3] >= 1 and x[2] == 0, data)
        out['rudder'] = [Joystick(x[0]) for x in rudders]
        return out

#@asyncio.coroutine
#def event_loop():
#    while True:
#        print('{}:{}:{}'.format(
#            axes[evdev.ecodes.ABS_X],
#            axes[evdev.ecodes.ABS_Y],
#            axes[evdev.ecodes.ABS_Z]))
#        yield from asyncio.sleep(0.25)
#
#asyncio.async(event_loop())
#
#loop = asyncio.get_event_loop()
#loop.run_forever()

