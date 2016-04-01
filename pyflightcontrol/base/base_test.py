import pyflightcontrol
import pyflightcontrol.base
import pygame
import time
import random

state = pyflightcontrol.AircraftState()

def main_loop():
    # Initialize GUI
    pygame.init()
    screensz = 1024
    screen = pygame.display.set_mode((screensz, screensz))
    pfd = pyflightcontrol.base.PFD(screensz, screensz)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise
        surf = pfd.render(state)
        screen.blit(surf, (0, 0))
        pygame.display.flip()
        time.sleep(0.1)

