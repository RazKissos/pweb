#!/usr/bin/python3
from colors import COLOR_MANAGER
import Data

COLOR = COLOR_MANAGER.color(255, 0, 255)


def check(data: Data.Data):
    print(COLOR + COLOR_MANAGER.BOLD + "- CSRF check:" + COLOR_MANAGER.ENDC)
    print(COLOR + "\tnope, nothing yet")
