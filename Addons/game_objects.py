import pygame as pg
import json
from Addons.settings import *

class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)

    

    
    
    def draw(self, screen):
        if DEBUG:
            pg.draw.rect(screen, (255, 0, 0), self.rect, 2)