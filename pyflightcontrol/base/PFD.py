import pygame
import pygame.freetype
import math
import numpy
from .font import getfont_mono_obj
from .indicator import Indicator
from .attitude import AttitudeIndicator

def _rnd(x):
    return int(round(x))

class PFD(object):
    def __init__(self, width, height):
        self._width = width
        self._height = height
        self._fontobj = getfont_mono_obj()
        self._attitude = AttitudeIndicator(width, height, 60.0)
        self._init_compass()
        self._airspd = Indicator(int(self._width*0.15),
                int(self._height*0.75), 50, 999, [(10, 0.2), (5, 0.1)],
                (10, 0.4, 0.15))
        
    def _init_compass(self):
        # Configuration Parameters
        self._compassfov = 70.0
        self._compasswidth = self._width*0.6
        compasscol = (0, 0, 0, 128) # 50% alpha black
        # Computed Parameters
        self._compassscale = self._compasswidth / self._compassfov
        self._compasswidth_s = (360+self._compassfov*2)*self._compassscale
        self._compasswidth_s = int(self._compasswidth_s)
        self._compassheight = int(self._width*0.08)
        # Make surface
        self._compass = pygame.Surface((self._compasswidth_s,
                self._compassheight), pygame.SRCALPHA)
        self._compass.fill(compasscol)
        # Draw tickmarks
        h_maj = int(self._compassheight*0.2)
        h_min = int(self._compassheight*0.1)
        for i in range(-40, 360+40):
            offset = self._compassscale*(self._compassfov+i)
            # calculate displayed bearing
            b = i % 360
            if b == 0:
                b = 360
            # determine height of tickmark (if any)
            h = 0
            if b % 10 == 0:
                h = h_maj
            elif b % 5 == 0:
                h = h_min
            # Draw tickmark (if any)
            if h != 0:
                pygame.draw.line(self._compass, (255,255,255,255),
                        (offset, 0), (offset, h))
                pygame.draw.line(self._compass, (255,255,255,255),
                        (offset, self._compassheight - h),
                        (offset, self._compassheight))
            # Draw bearing indicator
            if b % 30 == 0:
                txt = '{:02d}'.format(b // 10)
                (txt_surf, txt_rect) = self._fontobj.render(txt,
                        (255,255,255), size=int(self._compassheight*0.5))
                h_offset = int((self._compassheight - txt_rect.height)/2)
                x_offset = offset - int(txt_rect.width/2)
                self._compass.blit(txt_surf, (x_offset, h_offset))
    

    def render(self, brng, pitch, roll):
        surf = pygame.Surface((self._width, self._height))
        self._render_attitude(surf, pitch, roll)
        self._render_compass(surf, brng)
        self._render_airspeed(surf, 100.0)
        return surf

    def _render_attitude(self, surf, pitch, roll):
        ind = self._attitude.render(pitch, roll)
        surf.blit(ind, (0, 0))

    def _render_airspeed(self, surf, spd):
        ind = self._airspd.render(spd)
        surf.blit(ind, (int(self._width*0.05), int(self._height*0.1)))

    def _render_compass(self, surf, brng):
        # Colors
        windowcol = (255, 255, 0)
        windowbg = (0, 0, 0)
        boxcol = (255, 255, 255)
        txtcol = (255, 255, 255)
        # Calculate offsets
        y_offset = int(self._height - 1.5*self._compassheight)
        x_offset = int((self._width - self._compasswidth) / 2)
        b_offset = int(self._compassscale*(0.5*self._compassfov+brng))
        # Draw Compass
        surf.blit(self._compass, (x_offset, y_offset),
                area=pygame.Rect(b_offset, 0,
                self._compasswidth, self._compassheight))
        # Draw Bounding Box
        bord_w = 2
        rect = pygame.Rect(x_offset - bord_w, y_offset - bord_w,
                self._compasswidth + bord_w, self._compassheight + bord_w)
        pygame.draw.rect(surf, boxcol, rect, 2)
        # Bearing Indicator Window:
        # Line
        bord_w = 3
        middle = self._width // 2
        pygame.draw.line(surf, windowcol, (middle, y_offset),
                (middle, y_offset + self._compassheight), bord_w)
        # offset coordinates
        y_offset += self._compassheight // 8
        y_offset_ind = y_offset - self._compassheight // 3
        # Text
        brng_int = _rnd(brng)
        if brng_int == 0:
            brng_int = 360
        txt = '{:03d}'.format(brng_int)
        (txt_surf, txt_rect) = self._fontobj.render(txt,
                txtcol, size=int(self._compassheight*0.7))
        # Triangle
        pad = 8
        center_offset = txt_rect.width // 2 + pad + bord_w
        tripoints = [
                (middle, y_offset),
                (middle - center_offset, y_offset_ind),
                (middle + center_offset, y_offset_ind)]
        pygame.draw.polygon(surf, windowcol, tripoints)
        rect = pygame.Rect(middle - txt_rect.width // 2 - pad,
                           y_offset_ind - txt_rect.height - pad*2,
                           txt_rect.width + pad*2,
                           txt_rect.height + pad*2)
        rect_bord = pygame.Rect(rect)
        rect_bord.width += bord_w
        rect_bord.height += bord_w
        rect_bord.left -= 2
        rect_bord.top -= 2
        pygame.draw.rect(surf, windowcol, rect_bord, bord_w)
        pygame.draw.rect(surf, windowbg, rect)
        surf.blit(txt_surf, (rect.left + pad, rect.top + pad))


