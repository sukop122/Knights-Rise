import pygame as pg
import sys, json, os
import random
from Addons.settings import *
from Addons.player import Player
from Addons.game_objects import Platform
from Addons.utility import load_platforms, load_level_data

levels = [
        {
        "map":"assets/ldtk/lvl_1/simplified/Level_0/_composite.png" 
        },
    {
        "map":"assets/ldtk/lvl_1/simplified/Level_1/_composite.png"
        },
    {    
        "map":"assets/ldtk/lvl_1/simplified/Level_2/_composite.png"
        }     
    ]
current_level = 0

os.chdir(os.path.dirname(os.path.abspath(__file__)))





pg.init()




screen = pg.display.set_mode((screen_width, screen_height))

game_state = "playing"

WIN_ZONE = pg.Rect(784,32, 64,64)

winscreen = pg.image.load("assets/screens/winscreen.png").convert_alpha()

clock = pg.time.Clock()

running = True

current_map, platform = load_level_data(levels[current_level])

sheet = pg.image.load("assets/dataset/brackey/sprites/knight.png").convert_alpha()

player = Player(380, (screen_height - 200), sheet)

while running:
    screen.fill((30, 30, 30))

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            exit()
    
    if game_state == "playing":
        screen.blit(current_map,(0, 0))

        keys = pg.key.get_pressed()

        player.update(keys, platform, current_level)

        if player.y + player.height < 0 and current_level < len(levels) -1:
            current_level += 1
            current_map, platform = load_level_data(levels[current_level])
            player.y = screen_height - player.height - 10

        # Fall through to previous level
        elif player.y > screen_height + 200 and current_level > 0:
            current_level -= 1
            current_map, platform = load_level_data(levels[current_level])

            player.y = player.y - screen_height
        player.draw(screen)
        player.draw_coords(screen)   

        for plat in platform:
            plat.draw(screen)


        if current_level == 2 and player.rect.colliderect(WIN_ZONE):
            game_state = "win"

    elif game_state == "game over":
        pass
    

    elif game_state == "win":
        screen.blit(winscreen, (0,0))
        
    pg.display.update()
    clock.tick(60)
pg.quit()
    
