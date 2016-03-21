from . import indicator

class AirspeedIndicator(indicator.Indicator):
    def __init__(self, width, height):
        opts = indicator.IndicatorOptions(50, 999, 1)
        opts.addTick(10, 0.2)
        opts.addTick(5, 0.1)
        opts.setLabelProperties(10, 0.3, 0.25)
        super().__init__(width, height, opts)
