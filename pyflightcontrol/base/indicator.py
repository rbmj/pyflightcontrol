import pygame
import pygame.freetype
import math
from .font import getfont_mono_obj

tickcol = (255, 255, 255)
bordercol = (128, 128, 128)
rotorcol = (255, 255, 255)
bgcol = (0, 0, 0, 128)

def centerblit(to, loc, frm):
    loc = (loc[0], loc[1] - (frm.get_height() // 2))
    to.blit(frm, loc)

class IndicatorOptions(object):
    def __init__(self, fov, indmax, interval, ticks=[], txttick=(0, 0, 0)):
        self.fov = fov
        self.indmax = indmax
        self.ticks = ticks
        self.txttick = txttick
        self.interval = interval

    def addTick(self, interval, length):
        self.ticks.append((interval, length))

    def setLabelProperties(self, interval, length, offset):
        self.txttick = (interval, length, offset)

class Rotor(object):
    def __init__(self, font, fontsize, linespace, mag, wnd, nxt, surf=None):
        # determine digit size
        (_, rect) = font.render('a', rotorcol, size=fontsize)
        self._charwidth = rect.width
        self._charheight = rect.height
        # save variables
        self._font = font
        self._fontsize = fontsize
        self._linespace = linespace
        self._mag = mag
        self._window = wnd
        self._nxt = nxt
        self._surf = surf
        if self._surf is None:
            # generate surface
            self._surf = pygame.Surface((self._charwidth,
                    self._charheight*linespace*21), pygame.SRCALPHA)
            self._surf.fill((0, 0, 0, 0))
            for i in range(1,21):
                (t, _) = font.render(str(int(i % 10)), rotorcol, size=fontsize)
                centerblit(self._surf, (0, self._get_offset(i, True)), t)
            
    def _get_offset(self, ind, raw=False):
        if not raw:
            indraw = ind
            ind = ind // self._mag
            mod = int(ind % 10)
            ind = mod if (ind < 10) else (10 + mod)
            ind = ind + self._nxt.getNextOffset(indraw)
        return (self._surf.get_height() - 
                int((0.5+ind) * self._linespace * self._charheight))

    def getNextOffset(self, ind):
        rawind = ind
        ind = ind // self._mag
        ind = ind % 10
        if ind == 9:
            return self._nxt.getNextOffset(rawind)
        return 0

    def renderToCenter(self, surf, loc, ind):
        off = self._get_offset(ind)
        height = int(self._charheight*self._window*1.5)
        loc = (loc[0], loc[1] - height//2)
        surf.blit(self._surf, loc, area=pygame.Rect(
                0, off - height//2, self._charwidth, height))

    @classmethod
    def createSeries(cls, numrotors, wnd, small):
        rotors = [small]
        surf = None
        mag = small.getMagnitude()
        for i in range(numrotors):
            rotors.append(cls(small.getFont(), small.getFontSize(),
                    small.getLinespace(), mag, wnd, rotors[-1], surf))
            surf = rotors[-1]._surf
            mag = mag * 10
        return rotors[::-1]


class SmallRotor(object):
    def __init__(self, font, fontsize, linespace, mag, wnd, interval):
        # determine digit size
        (_, rect) = font.render('a', rotorcol, size=fontsize)
        self._charwidth = rect.width
        self._charheight = rect.height
        # save variables
        self._font = font
        self._fontsize = fontsize
        self._linespace = linespace
        self._mag = mag
        self._window = wnd
        self._interval = interval
        # generate surface
        self._surf = pygame.Surface((self._charwidth,
                self._charheight*linespace*21), pygame.SRCALPHA)
        self._surf.fill((0, 0, 0, 0))
        for i in range(mag//interval + 1):
            num = (i * interval) % mag
            (t, _) = font.render(str(int(num)), rotorcol, size=fontsize)
            centerblit(self._surf, (0, self._get_offset(i*interval, True)), t)
    
    def _get_offset(self, ind, raw=False):
        if not raw:
            ind = ind % self._mag
        ind = ind / self._interval
        return (self._surf.get_height() - 
                int((0.5+ind) * self._linespace * self._charheight))

    def getNextOffset(self, ind):
        ind = ind % self._mag
        ind = ind / self._interval
        m = (self._mag // self._interval) - 1
        if ind > m:
            return ind - m
        return 0

    def getFont(self):
        return self._font

    def getMagnitude(self):
        return self._mag

    def getFontSize(self):
        return self._fontsize

    def getLinespace(self):
        return self._linespace
    
    def renderToCenter(self, surf, loc, ind):
        off = self._get_offset(ind)
        height = int(self._charheight*self._window*1.5)
        loc = (loc[0], loc[1] - height//2)
        surf.blit(self._surf, loc, area=pygame.Rect(
                0, off - height//2, self._charwidth, height))

class RotatingIndicator(object):
    def __init__(self, font, width, numdigits, interval, left):
        linespace = 2
        self._linespace = linespace
        # Determine max magnitude of small digits and
        # number of small digits
        smallmag = 1
        for i in range(numdigits):
            smallmag = 10*smallmag
            if smallmag % interval == 0:
                break
        else:
            raise Exception('Logic error') #FIXME
        # determine fontsize
        self._stride = 1.2
        (_, rect) = font.render('a', rotorcol, size=100)
        charwidth = rect.width/100
        charheight = rect.height/100
        fontsize = int((width/(numdigits+0.5) * 0.6 / self._stride) / charwidth)
        charwidth = self._stride*charwidth*fontsize
        charheight = charheight*fontsize*1.5
        # set variables
        self._small_digits = i + 1
        self._large_digits = numdigits - self._small_digits
        self._numdigits = numdigits
        self._interval = interval
        self._left = left
        self._width = width
        self._height = int(3.7*charheight)
        self._charwidth = charwidth
        self._charheight = charheight
        # create rotors
        small = SmallRotor(font, fontsize, linespace, smallmag, 2.4, interval)
        self._rotors = Rotor.createSeries(self._large_digits, 1.2, small)
        if left:
            points = [
                    (width*0.9, 0),
                    (width*0.75, 0.5*charheight),
                    (width*0.75, 1.75*charheight),
                    (width*0.75 - (self._small_digits+1)*charwidth, 1.75*charheight),
                    (width*0.75 - (self._small_digits+1)*charwidth, charheight),
                    (width*0.075, charheight)]

        else:
            points = [
                    (width*0.1, 0),
                    (width*0.25, 0.5*charheight),
                    (width*0.25, charheight),
                    (width*0.925 - (self._small_digits+1)*charwidth, charheight),
                    (width*0.925 - (self._small_digits+1)*charwidth, 1.75*charheight),
                    (width*0.925, 1.75*charheight)]
        points = points + [(x, -y) for (x, y) in points[:0:-1]]
        self._points = [(int(x), (self._height // 2) - int(y)) for (x, y) in points]

    def render(self, ind):
        surf = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (0, 0, 0), self._points)
        pygame.draw.polygon(surf, (255, 255, 255), self._points, 2)
        if self._left:
            pos = int(self._width*0.75 - (self._numdigits+0.5)*self._charwidth
                    + self._charwidth - self._charwidth/self._stride)
        else:
            pos = int(self._width*0.925 - (self._numdigits+0.5)*self._charwidth
                    + self._charwidth - self._charwidth/self._stride)
        i = 0
        pos = pos + int((self._charwidth - self._charwidth/self._stride)/2)
        for rotor in self._rotors:
            cpos = pos + int(i * self._charwidth)
            rotor.renderToCenter(surf, (cpos, self._height // 2), ind);
            i = i + 1
        return surf

class Indicator(object):
    def __init__(self, width, height, indopts, left=True):
        self._fontobj = getfont_mono_obj()
        # calculate max number of digits
        maxdigits = 0
        tmp = indopts.indmax
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
        # misc parameters
        tickheight = 2
        self._interpgain = 0.5 # smoother gain - disable with 1

        # Set parameters/state
        self._left = left
        self._width = width
        self._height = height
        self._fov = indopts.fov
        self._indmax = indopts.indmax
        self._maxdigits = maxdigits
        self._scale = self._height / self._fov
        self._fontsize = int(
                (width/maxdigits * indopts.txttick[1]) / charwidth)
        self._border = 2
        self._value = 0.0

        # Create rotor indicator
        self._indicator = RotatingIndicator(self._fontobj, width, 
                maxdigits, indopts.interval, left)

        # Setup base surface
        self._base_height = height + math.ceil(self._scale*indopts.indmax)
        self._base_surf = pygame.Surface((width, self._base_height),
                pygame.SRCALPHA)
        self._base_surf.fill(bgcol)
        
        # draw indicator strip
        indstrip = int(0.865*self._width)
        indx = self._x(indstrip)
        pygame.draw.line(self._base_surf, tickcol, (indx, 0),
                (indx, self._offset(0)), int(0.03*self._width))
        # draw tick marks
        for i in range(indopts.indmax):
            offset = self._offset(i)
            tick_width = 0
            for (interval, w) in indopts.ticks:
                if i % interval == 0:
                    tick_width = w
                    break
            if tick_width != 0:
                pygame.draw.line(self._base_surf, tickcol,
                        (self._x(int(0.88*width)), offset),
                        (self._x(int((0.88-w)*width)), offset), tickheight)
            if indopts.txttick[0] != 0 and i % indopts.txttick[0] == 0:
                if self._fontsize == 0:
                    continue
                txt = txttick_fmt.format(i)
                (txt_surf, txt_rect) = self._fontobj.render(txt, tickcol,
                        size=self._fontsize)
                self._blit(self._base_surf, int(width*indopts.txttick[2]),
                    offset - txt_rect.height // 2, txt_surf)

    def render(self, ind):
        self._value = (self._interpgain*ind + 
                (1-self._interpgain)*self._value)
        surf = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        offset = self._offset(ind)
        area=pygame.Rect(0, offset - self._height // 2,
                         self._width, self._height)
        surf.blit(self._base_surf, (0, 0), area=area)
        centerblit(surf, (0, self._height // 2), self._indicator.render(ind))
        # draw border
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

