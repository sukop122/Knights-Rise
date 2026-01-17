import pygame as pg
import sys, json, os
import random
from Addons.settings import *
from Addons.player import Player
from Addons.game_objects import Platform
from Addons.utility import load_platforms

    

os.chdir(os.path.dirname(os.path.abspath(__file__)))



pg.init()

screen = pg.display.set_mode((screen_width, screen_height))

clock = pg.time.Clock()
running = True

map = pg.image.load("assets/ldtk/lvl_1/simplified/Level_0/_composite.png")
sheet = pg.image.load("assets/dataset/brackey/sprites/knight.png").convert_alpha()

player = Player(400, (screen_height - 200), sheet)
platform = load_platforms("assets/ldtk/lvl_1/simplified/Level_0/data.json")

while running:
    screen.fill((30, 30, 30))

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    screen.blit(map,(0, 0))
    
    keys = pg.key.get_pressed()

    player.update(keys, platform)
    player.draw(screen)
    player.draw_coords(screen)   

    for plat in platform:
        plat.draw(screen)

    pg.display.update()
    clock.tick(60)
    