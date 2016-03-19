import sys
import numpy
import math
import pygame
from pathlib import Path

def getfont_mono(pathstr=None):
    if pathstr is None:
        d = Path(sys.argv[0]).resolve().parent
        f = 'liberation_mono.ttf'
        paths = [d / f,
                 d.parent / 'share' / 'pyflightcontrol' / f,
                 Path('.').resolve() / f]
        paths = filter(lambda x: x.exists(), paths)
        for x in paths:
            pathstr = str(x)
            return pathstr
        raise FileNotFoundError()
    return pathstr

# Font notes: width is ~60% of size, height is ~114% of size
fontfile = getfont_mono()
fontobj_dict = {}

class text(object):
    def __init__(self, text, color, size=10, rotation=0):
        self._fontobj = fontobj_dict.get(size)
        if self._fontobj is None:
            self._fontobj = pygame.font.Font(fontfile, size)
            fontobj_dict[size] = self._fontobj
        self._text = self._fontobj.render(text, True, color)
        rect = self._text.get_rect()
        txt_x = rect.width/2.0
        txt_y = rect.height/2.0
        if rotation != 0:
            self._text = pygame.transform.rotate(self._text, rotation)
            vec = numpy.array([math.cos(rotation*math.pi/180),
                              -math.sin(rotation*math.pi/180)])
            self._left = -txt_x*vec
            self._right = txt_x*vec
            rect = self._text.get_rect()
            vec = numpy.array([rect.width/2.0, rect.height/2.0])
            self._left = vec + self._left
            self._right = vec + self._right
        else:
            self._left = numpy.array((0, txt_y))
            self._right = numpy.array((txt_x*2, txt_y))
    
    def blitTo(self, surf, loc, left=True):
        loc = numpy.array(loc)
        if left:
            loc = loc - self._left
        else:
            loc = loc - self._right
        loc = (int(round(loc[0])), int(round(loc[1])))
        surf.blit(self._text, loc)
