import pyflightcontrol as pfc
import pygame
import time
import random
from .PFD import PFD

def main_loop():
    # Initialize GUI
    pygame.init()
    screensz = 720
    screen = pygame.display.set_mode((screensz, screensz))
    pfd = PFD(screensz, screensz)
    pitch = 0
    roll = 0
    brng = 60
    alt = 0.0
    spd = 0.0
    while True:
        spd = spd + 0.1
        alt = alt + 2.5
        brng = (brng - 1)
        brng = brng + random.gauss(0, 1)
        brng = brng % 360
        roll = roll + random.gauss(0, 0.25)
        pitch = pitch + random.gauss(0, 0.25)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise
        surf = pfd.render(brng, pitch, roll, spd, alt)
        screen.blit(surf, (0, 0))
        pygame.display.flip()
        time.sleep(0.1)

