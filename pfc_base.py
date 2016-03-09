import pyflightcontrol.base.base as base
import pygame

(loop, actions) = base.get_main_loop()

try:
    loop.run_forever()
finally:
    for act in actions:
        act.cancel()
    pygame.quit()
    loop.close()
