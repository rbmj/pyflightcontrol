import pyflightcontrol as pfc
import pygame
import time
import random
from .PFD import PFD

def main_loop():
    # Initialize GUI
    pygame.init()
    screensz = 640
    screen = pygame.display.set_mode((screensz, screensz))
    pfd = PFD(screensz, screensz)
    pitch = 0
    roll = 0
    brng = 60
    while True:
        brng = (brng - 1)
        brng = brng + random.gauss(0, 1)
        brng = brng % 360
        roll = roll + random.gauss(0, 0.25)
        pitch = pitch + random.gauss(0, 0.25)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise
        surf = pfd.render(brng, pitch, roll)
        screen.blit(surf, (0, 0))
        pygame.display.flip()
        time.sleep(0.1)

