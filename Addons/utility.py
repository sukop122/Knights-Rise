import pygame as pg, json
from Addons.game_objects import Platform
import os




def image_cutter(sheet, frame_x, frame_y, width, height, scale):
    img = pg.Surface((width, height),pg.SRCALPHA)
    img.blit(sheet, (0, 0), ((frame_x * width),(frame_y * height), width, height))
    img = pg.transform.scale(img,(width*scale, height*scale))
    return img

def load_animation(sheet, row, frame_count, width, height, scale):
    frames = []
    for i in range(frame_count):
        frame = image_cutter(sheet, i, row, width, height, scale)
        frames.append(frame)
    return frames

def load_platforms(path):
    with open(path, "r") as f:
        data = json.load(f)


    platforms = []

    for entity in data["entities"]["Platform"]:
        x = entity["x"]
        y = entity["y"]
        w = entity["width"]
        h = entity["height"]
        platforms.append(Platform(x, y, w, h))

    return platforms
    