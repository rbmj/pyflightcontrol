import pygame
from .font import getfont_mono_obj

def _rnd(x):
    return int(round(x))

class CompassIndicator(object):
    def __init__(self, width, height, fov):
        self._fov = fov
        self._width = width
        self._height = height // 3
        self._render_height = height
        self._fontobj = getfont_mono_obj()

        compasscol = (0, 0, 0, 128) # 50% alpha black
        # Computed Parameters
        self._scale = self._width / self._fov
        self._base_width = (360+self._fov*2)*self._scale
        self._base_width = int(self._base_width)
        # Make surface
        self._base_surf = pygame.Surface((self._base_width,
                self._height), pygame.SRCALPHA)
        self._base_surf.fill(compasscol)
        # Draw tickmarks
        h_maj = int(self._height*0.2)
        h_min = int(self._height*0.1)
        for i in range(-40, 360+40):
            offset = self._scale*(self._fov+i)
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
                pygame.draw.line(self._base_surf, (255,255,255,255),
                        (offset, 0), (offset, h))
                pygame.draw.line(self._base_surf, (255,255,255,255),
                        (offset, self._height - h),
                        (offset, self._height))
            # Draw bearing indicator
            if b % 30 == 0:
                txt = '{:02d}'.format(b // 10)
                (txt_surf, txt_rect) = self._fontobj.render(txt,
                        (255,255,255), size=int(self._height*0.5))
                h_offset = int((self._height - txt_rect.height)/2)
                x_offset = offset - int(txt_rect.width/2)
                self._base_surf.blit(txt_surf, (x_offset, h_offset))
    
    def render(self, brng):
        surf = pygame.Surface((self._width, self._render_height),
                pygame.SRCALPHA)
        # Colors
        windowcol = (255, 255, 255)
        windowbg = (0, 0, 0)
        boxcol = (128, 128, 128)
        txtcol = (255, 255, 255)
        # Calculate offsets
        y_offset = int(self._render_height - self._height)
        b_offset = int(self._scale*(0.5*self._fov+brng))
        # Draw Compass
        surf.blit(self._base_surf, (0, y_offset),
                area=pygame.Rect(b_offset, 0,
                self._width, self._height))
        # Draw Bounding Box
        bord_w = 2
        rect = pygame.Rect(0, y_offset, self._width - bord_w // 2,
                self._height - bord_w // 2)
        pygame.draw.rect(surf, boxcol, rect, bord_w)
        # Bearing Indicator Window:
        # Line
        bord_w = 3
        middle = self._width // 2
        pygame.draw.line(surf, windowcol, (middle, y_offset),
                (middle, y_offset + self._height), bord_w)
        # offset coordinates
        y_offset += self._height // 3
        y_offset_ind = y_offset - self._height // 4
        # Text
        brng_int = _rnd(brng)
        if brng_int == 0:
            brng_int = 360
        txt = '{:03d}'.format(brng_int)
        (txt_surf, txt_rect) = self._fontobj.render(txt,
                txtcol, size=int(self._height*0.7))
        # Triangle
        pad = 8
        center_offset = txt_rect.width // 2 + pad
        arrow_offset = self._height // 8
        boxheight = txt_rect.height + pad*2
        tripoints = [
                (middle, y_offset),
                (middle - arrow_offset, y_offset_ind),
                (middle - center_offset, y_offset_ind),
                (middle - center_offset, y_offset_ind - boxheight),
                (middle + center_offset, y_offset_ind - boxheight),
                (middle + center_offset, y_offset_ind),
                (middle + arrow_offset, y_offset_ind)]
        pygame.draw.polygon(surf, windowbg, tripoints)
        pygame.draw.polygon(surf, windowcol, tripoints, bord_w)
        surf.blit(txt_surf, (middle - center_offset + pad,
            y_offset_ind - boxheight + pad))
        return surf
