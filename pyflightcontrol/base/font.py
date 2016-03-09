import sys
from pathlib import Path

def getfont_mono():
    d = Path(sys.argv[0]).resolve().parent
    f = 'liberation_mono.ttf'
    paths = [d / f, d.parent / 'share' / 'pyflightcontrol' / f]
    paths = filter(lambda x: x.exists(), paths)
    for x in paths:
        return str(x)
    raise FileNotFoundError()

fontfile = getfont_mono()

class text(object):
    # render font
    # rotate it
    # blit it
