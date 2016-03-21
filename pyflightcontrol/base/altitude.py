from . import indicator

# Altimeter would be more correct, but for consistency's sake...
class AltitudeIndicator(indicator.Indicator):
    def __init__(self, width, height):
        opts = indicator.IndicatorOptions(600, 19999, 20)
        opts.addTick(100, 0.2)
        opts.addTick(20, 0.1)
        opts.setLabelProperties(100, 0.4, 0.15)
        super().__init__(width, height, opts, False)
