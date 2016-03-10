import pygame
import pygame.freetype
import math
import numpy
from .font import getfont_mono

def _rnd(x):
    return int(round(x))

def _sgnmatch(val, match):
    if match < 0:
        return 0
    return val

# Returns either [m, b] in y = mx + b, or [c] in x = c
def _eqnline(p1, p2):
    x1 = p1.item(0)
    y1 = p1.item(1)
    x2 = p2.item(0)
    y2 = p2.item(1)
    if x2 == x1:
        return [x2]
    m = (y2-y1)/(x2-x1)
    b = y1 - m*x1
    return [m, b]

def _intercept_at_x(l, x):
    if len(l) == 1:
        return None
    y = l[0]*x+l[1]
    return _makecoord(x, y)

def _intercept_at_y(l, y):
    if len(l) == 1:
        return _makecoord(l[0], y)
    if l[0] == 0:
        return None
    x = (y - l[1])/l[0]
    return _makecoord(x, y)

def _makecoord(x, y):
    return numpy.matrix([[x], [y], [1]])

def _makeroll(phi):
    phi = phi*math.pi/180 # radian conversion
    return numpy.matrix([[math.cos(phi), -math.sin(phi), 0],
                         [math.sin(phi), math.cos(phi) , 0],
                         [0            , 0             , 1]])

def _makepitch(theta):
    return numpy.matrix([[1, 0, 0], [0, 1, -theta], [0, 0, 1]])

def _gettheta(p, offx=0, offy=0):
    return math.atan2(p[1] + offy, p[0] + offx)

class PFD(object):
    def __init__(self, width, height):
        self._width = width
        self._height = height
        self._widthfov = 60.0
        self._heightfov = (height/width)*self._widthfov
        self._scalefactor = width/self._widthfov
        self._fontobj = pygame.freetype.Font(getfont_mono())
        self._init_attitude()
        self._init_compass()
        
    def _init_attitude(self):
        self._pitchlines = []
        self._pitchtextsz = self._width // 50
        major = True
        majorwidth = 0.25*self._widthfov
        minorwidth = 0.75*majorwidth
        for p in range(-90, 91, 5):
            width = majorwidth
            if not major:
                width = minorwidth
            start = _makecoord(-width, p)
            stop = _makecoord(width, p)
            txtmark = _makecoord(width*1.1, p)
            self._pitchlines.append((start, stop, p, txtmark))
            major = not major
        self._horizon = (_makecoord(-self._widthfov, 0),
                         _makecoord(self._widthfov, 0))

    def _init_compass(self):
        self._compassfov = 70.0
        self._compasswidth = self._width*0.6
        self._compassscale = self._compasswidth / self._compassfov
        self._compasswidth_s = (360+self._compassfov*2)*self._compassscale
        self._compasswidth_s = int(self._compasswidth_s)
        self._compassheight = int(self._width*0.08)
        self._compass = pygame.Surface((self._compasswidth_s,
                self._compassheight), pygame.SRCALPHA)
        self._compass.fill((0, 0, 0, 128))
        h_maj = int(self._compassheight*0.2)
        h_min = int(self._compassheight*0.1)
        for i in range(-40, 360+40):
            offset = self._compassscale*(self._compassfov+i)
            b = 360 if i == 0 else i % 360
            h = 0
            if b % 10 == 0:
                h = h_maj
            elif b % 5 == 0:
                h = h_min
            if h != 0:
                pygame.draw.line(self._compass, (255,255,255,255),
                        (offset, 0), (offset, h))
                pygame.draw.line(self._compass, (255,255,255,255),
                        (offset, self._compassheight - h),
                        (offset, self._compassheight))
            if b % 30 == 0:
                txt = '{:02d}'.format(b // 10)
                (txt_surf, txt_rect) = self._fontobj.render(txt,
                        (255,255,255), size=int(self._compassheight*0.5))
                h_offset = int((self._compassheight - txt_rect.height)/2)
                x_offset = offset - int(txt_rect.width/2)
                self._compass.blit(txt_surf, (x_offset, h_offset))
    
    def _drawpitchline(self, xform, surf, i, pitchcolor, roll):
        (start, end, p, txtl) = self._pitchlines[i]
        if p == 0:
            return
        start = xform*start
        end = xform*end
        txtl = xform*txtl
        start = (_rnd(start.item(0)*self._scalefactor + self._width/2),
                 _rnd(self._height/2 - start.item(1)*self._scalefactor))
        end = (_rnd(end.item(0)*self._scalefactor + self._width/2),
               _rnd(self._height/2 - end.item(1)*self._scalefactor))
        txtl = (_rnd(txtl.item(0)*self._scalefactor + self._width/2),
               _rnd(self._height/2 - txtl.item(1)*self._scalefactor))
        pygame.draw.line(surf, pitchcolor, start, end)
        pfx = '+' if p > 0 else '-'
        txt = pfx + str(abs(p))
        self._fontobj.render_to(surf, txtl, txt, pitchcolor,
                rotation=int(roll), size=self._pitchtextsz)

    def render(self, brng, pitch, roll):
        surf = pygame.Surface((self._width, self._height))
        self._render_horizon(surf, pitch, roll)
        self._render_compass(surf, brng)
        return surf

    def _render_compass(self, surf, brng):
        y_offset = int(self._height - 1.5*self._compassheight)
        x_offset = int((self._width - self._compasswidth) / 2)
        b_offset = int(self._compassscale*(0.5*self._compassfov+brng))
        surf.blit(self._compass, (x_offset, y_offset),
                area=pygame.Rect(b_offset, 0,
                self._compasswidth, self._compassheight))
        rect = pygame.Rect(x_offset - 2, y_offset - 2,
                self._compasswidth + 2, self._compassheight + 2)
        pygame.draw.rect(surf, (255,255,255), rect, 2)

        
    def _render_horizon(self, surf, pitch, roll):
        # Artificial horizon colors
        skycolor = (10, 112, 184)
        groundcolor = (223, 131, 3)
        referencecolor = (255, 255, 0)
        pitchcolor = (255, 255, 255)
        # Make artificial horizon transform matrix
        transform = _makeroll(roll)*_makepitch(pitch)

        # Transform points and determine intersections
        horizon = _eqnline(transform*self._horizon[0],
                transform*self._horizon[1])
        xinter = [_intercept_at_x(horizon, -self._widthfov/2),
                  _intercept_at_x(horizon, self._widthfov/2)]
        yinter = [_intercept_at_y(horizon, -self._heightfov/2),
                  _intercept_at_y(horizon, self._heightfov/2)]

        # Remove non-existent intersections
        xinter = filter(lambda x: x is not None, xinter)
        yinter = filter(lambda x: x is not None, yinter)

        # Determine if intersections are within the window bounds
        xinter = filter(lambda p: abs(p.item(1)) < self._heightfov/2, xinter)
        yinter = filter(lambda p: abs(p.item(0)) < self._widthfov/2, yinter)

        # Find intersection points in pixel space
        xinter = [(_sgnmatch(self._width, p.item(0)),
                   _rnd(self._height/2 - p.item(1)*self._scalefactor))
                   for p in xinter]
        yinter = [(_rnd(p.item(0)*self._scalefactor + self._width/2),
                   _sgnmatch(self._height, -p.item(1))) for p in yinter]
        intersect = xinter + yinter
        intersect = list(intersect)

        # Get corner coordinates and determine which are +/- pitch
        # FIXME:  This breaks near the corners
        pts = [_makecoord(-self._widthfov/2, -self._heightfov/2),
               _makecoord(-self._widthfov/2, self._heightfov/2),
               _makecoord(self._widthfov/2, self._heightfov/2),
               _makecoord(self._widthfov/2, -self._heightfov/2)]
        pts_abs = [transform.I*p for p in pts]
        pts_view = [(0, self._height), (0, 0), 
                    (self._width, 0), (self._width, self._height)]
        pos_idx = filter(lambda i: pts_abs[i].item(1) >= 0, range(len(pts)))
        pos_idx = list(pos_idx)
        neg_idx = filter(lambda i: i not in pos_idx, range(len(pts)))
        pts_pos = [pts_view[i] for i in pos_idx]
        pts_pos = pts_pos + intersect
        pts_neg = [pts_view[i] for i in neg_idx]
        pts_neg = pts_neg + intersect

        # Order the points for drawing
        sortkey = lambda x: _gettheta(x, -self._width/2, -self._height/2)
        pts_pos.sort(key=sortkey)
        pts_neg.sort(key=sortkey)
        
        # Draw artificial horizon
        if len(pts_pos) > 2:
            pygame.draw.polygon(surf, skycolor, pts_pos)
        if len(pts_neg) > 2:
            pygame.draw.polygon(surf, groundcolor, pts_neg)
        if len(intersect) == 2:
            pygame.draw.line(surf, pitchcolor, intersect[0],
                    intersect[1], 3)
        
        # Draw Pitch Lines
        nearest_pitch = 5*_rnd(pitch/5)
        pitchline_index = (nearest_pitch + 90)//5
        rng = range(pitchline_index - 5, pitchline_index + 6)
        rng = filter(lambda x: x >= 0 and x < len(self._pitchlines), rng)
        for i in rng:
            self._drawpitchline(transform, surf, i, pitchcolor, roll)
        
        # Draw Aircraft Attitude Reference
        arrow_width = self._width/10
        arrow_height = self._width/15
        pygame.draw.polygon(surf, referencecolor, [
            (self._width/2, self._height/2),
            (self._width/2 - arrow_width, self._height/2 + arrow_height),
            (self._width/2 + arrow_width, self._height/2 + arrow_height)])
        pygame.draw.line(surf, referencecolor,
            (self._width/2 - 3*arrow_width, self._height/2),
            (self._width/2 - 1.5*arrow_width, self._height/2), 5)
        pygame.draw.line(surf, referencecolor,
            (self._width/2 + 3*arrow_width, self._height/2),
            (self._width/2 + 1.5*arrow_width, self._height/2), 5)

