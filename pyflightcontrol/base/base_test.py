import pyflightcontrol as pfc
import pygame
import time
import random
from .PFD import PFD

state = pfc.AircraftState()

def main_loop():
    # Initialize GUI
    pygame.init()
    screensz = 1024
    screen = pygame.display.set_mode((screensz, screensz))
    pfd = PFD(screensz, screensz)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise
        surf = pfd.render(state)
        screen.blit(surf, (0, 0))
        pygame.display.flip()
        time.sleep(0.1)

