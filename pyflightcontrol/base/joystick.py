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
        for btn in self.enumerateButtons(resolve=False):
            self._buttons[btn] = 0
        for ax in self.enumerateAxes(resolve=False):
            self._axes[ax] = 0.0

    @asyncio.coroutine
    def _pump(self):
        while True:
            events = yield from self._dev.async_read()
            for event in events:
                if event.type == evdev.ecodes.EV_ABS:
                    self._axes[event.code] = event.value
                elif event.type == evdev.ecodes.EV_KEY:
                    self._buttons[event.code] = event.value
                    h = self._handlers.get(event.value)
                    if h:
                        h()

    def register(self):
        return asyncio.async(self._pump())

    def addButtonHandler(self, h, code):
        self._handlers[code] = h

    def getX(self):
        return self._axes[evdev.ecodes.ABS_X]

    def getY(self):
        return self._axes[evdev.ecodes.ABS_Y]

    def getZ(self):
        return self._axes[evdev.ecodes.ABS_Z]

    def getAxis(self, code):
        return self._axes[code]

    def getButton(self, code):
        return self._buttons[code]
    
    def enumerateButtons(self, resolve=True):
        cap = self._dev.capabilities(verbose=False, absinfo=False)
        try:
            btns = cap[evdev.ecodes.EV_KEY]
        except KeyError:
            return []
        if resolve:
            names = [name if isinstance(name, str) else name[-1]
                        for name in (evdev.ecodes.BTN[x] for x in btns)]
            return [x for x in zip(names, btns)]
        return btns

    def enumerateAxes(self, resolve=True):
        cap = self._dev.capabilities(verbose=False, absinfo=False)
        try:
            axes = cap[evdev.ecodes.EV_ABS]
        except KeyError:
            return []
        if resolve:
            names = [evdev.ecodes.ABS[x] for x in axes]
            return [x for x in zip(names, axes)]
        return axes

    @classmethod
    def autodetect(cls):
        out = {}
        devs = [evdev.InputDevice(d) for d in evdev.util.list_devices()]
        caps = [d.capabilities(verbose=False, absinfo=False) for d in devs]
        btns = [len(c.get(evdev.ecodes.EV_KEY, [])) for c in caps]
        axes = [len(c.get(evdev.ecodes.EV_ABS, [])) for c in caps]
        data = [x for x in zip(devs, caps, btns, axes)]
        sticks = filter(lambda x: x[3] >= 3 and x[3] <= 6 and x[2] > 1,
                data)
        out['stick'] = [cls(x[0]) for x in sticks]
        rudders = filter(lambda x: x[3] >= 1 and x[2] == 0, data)
        out['rudder'] = [cls(x[0]) for x in rudders]
        return out


