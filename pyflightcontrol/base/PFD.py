import pygame
from .attitude import AttitudeIndicator
from .compass import CompassIndicator
from .airspeed import AirspeedIndicator

class PFD(object):
    def __init__(self, width, height):
        self._width = width
        self._height = height
        self._attitude = AttitudeIndicator(width, height, 60.0)
        self._compass = CompassIndicator(int(width*0.6), int(height*0.3),
                70.0)
        self._airspd = AirspeedIndicator(int(width*0.15), int(height*0.7))
        self._spd = 0.0

    def render(self, brng, pitch, roll):
        self._spd = self._spd + 0.1
        surf = pygame.Surface((self._width, self._height))
        self._render_attitude(surf, pitch, roll)
        self._render_compass(surf, brng)
        self._render_airspeed(surf, self._spd)
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
