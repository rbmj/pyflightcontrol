import pygame
from .indicator import Indicator
from .attitude import AttitudeIndicator
from .compass import CompassIndicator

class PFD(object):
    def __init__(self, width, height):
        self._width = width
        self._height = height
        self._attitude = AttitudeIndicator(width, height, 60.0)
        self._compass = CompassIndicator(int(width*0.6), int(height*0.3),
                70.0)
        self._airspd = Indicator(int(self._width*0.15),
                int(self._height*0.75), 50, 999, [(10, 0.2), (5, 0.1)],
                (10, 0.4, 0.15))

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
        ind = self._compass.render(brng)
        surf.blit(ind, (int(self._width*0.2), int(self._height*0.65)))
