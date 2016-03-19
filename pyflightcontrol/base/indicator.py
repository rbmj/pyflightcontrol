import pygame
import pygame.freetype
import math
from .font import getfont_mono

tickcol = (255, 255, 255)
bordercol = (255, 255, 255)
bgcol = (0, 0, 0, 128)

class Indicator(object):
    # ticks is e.g. [(10, .2), (5, .1)] for 20% every 10, 10% every 5
    # indmax is max value
    # txttick is e.g. (100, .4, .3) for 40% width starting at 30% every 100
    def __init__(self, width, height, fov, indmax, ticks, txttick, left=True):
        self._fontobj = pygame.freetype.Font(getfont_mono())
        # calculate max number of digits
        maxdigits = 0
        tmp = indmax
        while tmp != 0:
            tmp = tmp // 10
            maxdigits = maxdigits + 1
        txttick_fmt = '{:' + str(maxdigits) + 'd}'
        # make height a round number
        if height % 2 == 1:
            height -= 1
        # determine font charwidth/size
        (_, rect) = self._fontobj.render('a', tickcol, size=100)
        charwidth = rect.width/100
        # random parameters
        tickheight = 2

        # Set parameters/state
        self._left = left
        self._width = width
        self._height = height
        self._fov = fov
        self._indmax = indmax
        self._maxdigits = maxdigits
        self._scale = self._height / self._fov
        self._fontsize = int((width/maxdigits*txttick[1])/charwidth)
        self._border = 2

        # Setup base surface
        self._base_height = height + math.ceil(self._scale*indmax)
        self._base_surf = pygame.Surface((width, self._base_height),
                pygame.SRCALPHA)
        self._base_surf.fill(bgcol)

        indstrip = int(0.865*self._width)
        indx = self._x(indstrip)
        pygame.draw.line(self._base_surf, tickcol, (indx, 0),
                (indx, self._offset(0)), int(0.03*self._width))
        for i in range(indmax):
            offset = self._offset(i)
            tick_width = 0
            for (interval, w) in ticks:
                if i % interval == 0:
                    tick_width = w
                    break
            if tick_width != 0:
                pygame.draw.line(self._base_surf, tickcol,
                        (self._x(int(0.88*width)), offset),
                        (self._x(int((0.88-w)*width)), offset), tickheight)
            if i % txttick[0] == 0:
                txt = txttick_fmt.format(i)
                (txt_surf, txt_rect) = self._fontobj.render(txt, tickcol,
                        size=self._fontsize)
                self._blit(self._base_surf, int(width*txttick[2]),
                    offset - txt_rect.height // 2, txt_surf)

    def render(self, ind):
        surf = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        offset = self._offset(ind)
        area=pygame.Rect(0, offset - self._height // 2,
                         self._width, self._height)
        surf.blit(self._base_surf, (0, 0), area=area)

        rect = surf.get_rect()
        rect.width -= self._border // 2
        rect.height -= self._border // 2
        pygame.draw.rect(surf, bordercol, rect, self._border)
        return surf

    def _offset(self, ind):
        return int(self._base_height -
                ((self._height // 2) + (self._scale*ind)))

    def _x(self, x):
        if self._left:
            return x
        return self._width - x
    
    def _blit(self, to, x, y, surf):
        if not self._left:
            x = (self._width - x) - surf.get_rect().width
        to.blit(surf, (x, y))

