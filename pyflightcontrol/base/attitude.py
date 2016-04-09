import pygame
import math
import numpy
from .font import getfont_mono_obj

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
    return numpy.matrix([[math.cos(phi),  math.sin(phi), 0],
                         [-math.sin(phi), math.cos(phi), 0],
                         [0            , 0             , 1]])

def _makepitch(theta):
    return numpy.matrix([[1, 0, 0], [0, 1, -theta], [0, 0, 1]])

def _maketrans(theta, phi):
    return numpy.matrix([[1, 0, phi], [0, 1, theta], [0, 0, 1]])

def _makescale(factor):
    return numpy.matrix([[factor, 0, 0], [0, factor, 0], [0, 0, 1]])

def _gettheta(p, offx=0, offy=0):
    return math.atan2(p[1] + offy, p[0] + offx)

class AttitudeIndicator(object):
    def __init__(self, width, height, fov):
        self._width = width
        self._height = height
        self._widthfov = fov
        self._heightfov = (height/width)*self._widthfov
        self._scalefactor = width/self._widthfov
        self._fontobj = getfont_mono_obj()

        # initialize pitchlines
        self._pitchlines = []
        self._pitchtextsz = self._width // 50
        major = True
        majorwidth = 0.15*self._widthfov
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
        self._deflect_center = _makecoord(0, 0)
        self._deflect_radius = self._widthfov*0.05
        self._deflect_lines = [
                [
                    _makecoord(self._deflect_radius, 0),
                    _makecoord(self._deflect_radius*2, 0)
                ],
                [
                    _makecoord(-self._deflect_radius, 0),
                    _makecoord(-2*self._deflect_radius, 0)
                ],
                [
                    _makecoord(0, self._deflect_radius),
                    _makecoord(0, 2*self._deflect_radius)
                ]
        ]
    
    def _drawpitchline(self, xform, surf, i, pitchcolor, roll):
        (start, end, p, txtl) = self._pitchlines[i]
        if p == 0:
            return
        start = xform*start
        end = xform*end
        txtl = xform*txtl
        # Line Start
        start = (_rnd(start.item(0)*self._scalefactor + self._width/2),
                 _rnd(self._height/2 - start.item(1)*self._scalefactor))
        # Line End
        end = (_rnd(end.item(0)*self._scalefactor + self._width/2),
               _rnd(self._height/2 - end.item(1)*self._scalefactor))
        # Text Location
        txtl = (_rnd(txtl.item(0)*self._scalefactor + self._width/2),
               _rnd(self._height/2 - txtl.item(1)*self._scalefactor))
        # Draw Line (antialiased)
        pygame.draw.aaline(surf, pitchcolor, start, end)
        # Draw Marker
        pfx = '+' if p > 0 else '-'
        txt = pfx + str(abs(p))
        self._fontobj.render_to(surf, txtl, txt, pitchcolor,
                rotation=int(roll), size=self._pitchtextsz)
    
    def render(self, pitch, roll, d_a, d_e, d_r):
        surf = pygame.Surface((self._width, self._height))
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
            pygame.draw.aaline(surf, pitchcolor, intersect[0],
                    intersect[1], 3)
        
        # Draw Pitch Lines
        nearest_pitch = 5*_rnd(pitch/5)
        pitchline_index = (nearest_pitch + 90)//5
        rng = range(pitchline_index - 5, pitchline_index + 6)
        rng = filter(lambda x: x >= 0 and x < len(self._pitchlines), rng)
        for i in rng:
            self._drawpitchline(transform, surf, i, pitchcolor, roll)
        
        # Draw Aircraft Attitude Reference
        arrow_width = self._width/15
        arrow_height = self._width/20
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
        
        # Draw control deflection reference
        scale = 0.15
        aileron_scale = 0.5
        xform_deflect = _makeroll(d_a*aileron_scale)
        xform_deflect = _maketrans(d_e*scale, d_r*scale)*xform_deflect
        xform_deflect = transform*xform_deflect
        xform_deflect = _makescale(self._scalefactor)*xform_deflect
        lines = [[(xform_deflect*pt).astype(numpy.int32) for pt in line]
                for line in self._deflect_lines] 
        return surf
