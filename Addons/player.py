from platform import platform
import pygame as pg
from Addons.settings import *
from Addons.utility import image_cutter, load_animation
#from Addons.game_objects import Platform

class Player(pg.sprite.Sprite):
    def __init__(self, x, y, sheet):
        super().__init__()
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.spawn_x = x
        self.spawn_y = y
        self.dead_counter = 0 

        
        self.vel_y = 0
        self.vel_x = 0
        self.jump_direction = 0
        self.on_ground = True
        self.charging = False
        self.charge_power = 0
        self.max_charge = 8
        self.in_air = False
        self.speed = 1.5

        self.state = "idle"
        self.index = 0
        self.animation_speed = 0.1
        self.facing_right = True
        self.collision = False

        self.hitbox_offset_x = 16
        self.hitbox_offset_y = 14
        self.hitbox_width = self.width + 4
        self.hitbox_height = self.height + 10
        

        self.rect = pg.Rect(self.x + self.hitbox_offset_x, self.y + self.hitbox_offset_y, self.hitbox_width, self.hitbox_height)


        self.animations = {
            "idle": image_cutter(sheet, 0, 0, 32, 32, 2),
            "charge": image_cutter(sheet, 1, 0, 32, 32, 2),
            "jump": image_cutter(sheet, 2, 0, 32, 32, 2),
            "bump": image_cutter(sheet, 3, 0, 32, 32, 2),
            "fall": image_cutter(sheet, 4, 0, 32, 32, 2),
            "run": load_animation(sheet, row=1, frame_count=3, width=32, height=32, scale=2)
            
        } 

    def respawn(self):
        self.x = self.spawn_x
        self.y= self.spawn_y
        self.dead_counter += 1
        self.vel_x = 0
        self.vel_y = 0
        self.state = "idle"
        self.in_air = False
        self.on_ground = False
        self.charge_power = 0
        self.rect.topleft = (self.x + self.hitbox_offset_x, self.y + self.hitbox_offset_y)
        

    def update(self, keys, platforms):

    #respawn
        if self.y > screen_height + 200:
            self.respawn()


     #Movement Left and Right on ground

        if not self.charging and self.on_ground:
            if keys[pg.K_a]:
                self.vel_x = -self.speed
                self.facing_right = False
                self.jump_direction = -1
                self.state = "run"
            
                
            elif keys[pg.K_d]:
                self.vel_x = self.speed
                self.facing_right = True
                self.jump_direction = 1
                self.state = "run"
            
            else:
                self.vel_x = 0
                self.state = "idle"
                

        

    #Jumping and Charging
     
        if self.on_ground:
            if keys[pg.K_SPACE]:
                self.charging = True
                self.charge_power += 0.2
            
                if self.charging == True:    
                    if keys[pg.K_a]:
                        self.facing_right = False
                        self.jump_direction = -1
                    elif keys[pg.K_d]:
                        self.facing_right = True
                        self.jump_direction = 1
                    elif keys[pg.K_w]:
                        self.jump_direction = 0
                
                if self.charge_power > self.max_charge:
                    self.charge_power = self.max_charge
                self.state = "charge"

            elif self.charging:
                self.jump(self.charge_power)
                self.charging = False
                self.charge_power = 0
            


        #Lock horizontal movement when charging or airborne
        if self.charging:
            self.vel_x = 0


    
    #Gravity
        gravity = 0.3
        self.vel_y += gravity

    #Aplication of velocities
        self.x += self.vel_x
        self.y += self.vel_y
        self.rect.topleft = (self.x + self.hitbox_offset_x, self.y + self.hitbox_offset_y)
    #Collision with screen borders
        if self.in_air:
            if self.x <= -self.width:
                self.x = 0
                self.collision = True
                if self.collision == True:
                    self.facing_right = True
                    self.state = "bump"
                    
                    self.vel_x *= -0.6
                    if self.y == screen_height - 50 - self.height:
                        self.collision = False
            


            elif self.x + self.width  >= screen_width - 50:
                self.x = screen_width - self.width - 50
                self.collision = True
                if self.collision == True:
                    self.facing_right = False
                    self.state = "bump"
                    self.vel_x *= -0.6
                    if self.y == screen_height - 50 - self.height:
                        self.collision = False
                      
    
    # #Ground level
    #     if self.y + self.height >= screen_height - 50: 
    #         self.y = screen_height - 50 - self.height
    #         self.vel_y = 0
    #         self.on_ground = True
    #         self.in_air = False
    #     else:
    #         self.on_ground = False
    #         self.in_air = True

        if self.vel_y > 0 and self.in_air and not self.collision:
            self.state = "fall"


        #Animation state changes - running
        if self.state == "run":
            self.index += self.animation_speed
            if self.index >= len(self.animations["run"]):
                self.index = 0
        
        #Collision with platforms
        self.x += self.vel_x
        self.y += self.vel_y

        self.rect.topleft = (self.x + self.hitbox_offset_x, self.y + self.hitbox_offset_y)

        landed = False
        for platform in platforms:
            next_rect = self.rect.move(0, self.vel_y)

            if (
                self.vel_y >= 0 and
                self.rect.bottom <= platform.rect.top + 10 and 
                next_rect.bottom >= platform.rect.top and
                self.rect.right > platform.rect.left and
                self.rect.left < platform.rect.right and
                self.state != "bump"
                
            ):
                #Landing on top
                self.y = platform.rect.top - self.hitbox_offset_y - self.hitbox_height
                self.vel_y = 0
                self.on_ground = True
                self.in_air = False
                self.state = "idle" if self.vel_x == 0 else "run"
                landed = True
                break
            
            
            #Bump from bottom
            elif (
                self.vel_y < 0 and
                self.rect.colliderect(platform.rect) and
                self.rect.top + self.vel_y <= platform.rect.bottom <= self.rect.top
            ):
                self.y = platform.rect.bottom - self.hitbox_offset_y
                self.vel_y = 0.5
                self.state = "bump"
                
            #Bump from left
            elif (
                self.vel_x > 0 and
                self.rect.right >= platform.rect.left and
                self.rect.left < platform.rect.left and
                self.rect.bottom > platform.rect.top + 10 and
                self.rect.top < platform.rect.bottom - 10
            ):
                self.x = platform.rect.left - self.hitbox_offset_x - self.hitbox_width
                self.vel_x *= -0.5
                self.state = "bump"

            #Bump from right
            elif (
                self.vel_x < 0 and
                self.rect.left <= platform.rect.right and
                self.rect.right > platform.rect.right and
                self.rect.bottom > platform.rect.top + 10 and
                self.rect.top < platform.rect.bottom - 10
            ):
                self.x = platform.rect.right - self.hitbox_offset_x
                self.vel_x *= -0.5
                self.state = "bump"
        if not landed:
                self.on_ground = False
                self.in_air = True


    #Jump function        
    def jump(self, power):
            self.collision = False
            side_force_multiplier = 0.5
            self.vel_y = -power
            self.vel_x = self.jump_direction * (power * side_force_multiplier)
            self.index = 0
            self.state = "jump"
            self.in_air = True
            self.on_ground = False

    def draw_charge_bar(self, screen):
        if self.charging:
            bar_width = 40
            bar_height = 6
            charge_ratio = self.charge_power / self.max_charge
            filled_width = int(bar_width * charge_ratio)

            #position above player
            bar_x = self.x + self.width // 2 - bar_width // 2
            bar_y = self.y - 15

            
            bg_rect = pg.Rect(bar_x, bar_y, bar_width, bar_height)
            pg.draw.rect(screen, (50, 50, 50), bg_rect)

            # vyplněná část
            fill_rect = pg.Rect(bar_x, bar_y, filled_width, bar_height)
            pg.draw.rect(screen, (200, 0, 0), fill_rect)
    
    


            



    def draw(self, screen):
        self.draw_charge_bar(screen)

        current_anim = self.animations[self.state]

        if isinstance(current_anim, list):
            frame = current_anim[int(self.index)]
        else:
            frame = current_anim  # single frame

        if self.facing_right:
            screen.blit(frame, (self.x, self.y-11))
        else:
            screen.blit(pg.transform.flip(frame, True, False), (self.x, self.y-11))

        if DEBUG:
            pg.draw.rect(screen, (255, 0, 0), self.rect, 2)



    def draw_coords (self, screen):
        font = pg.font.Font("assets/dataset/brackey/fonts/Jersey20-Regular.ttf", 24)

        text_X = font.render(f"X: {self.x}", False, "#FFFFFF")
        text_Y = font.render(f"Y: {self.y}", False, "#FFFFFF")

        text_velX = font.render(f"X: {self.vel_x}", False, "#FFFFFF")
        text_velY = font.render(f"Y: {self.vel_y}", False, "#FFFFFF")

        screen.blit(text_X, (screen_width-100, 30))
        screen.blit(text_Y, (screen_width-100, 50))

        screen.blit(text_velX, (screen_width-100, 80))
        screen.blit(text_velY, (screen_width-100, 100))

        screen.blit(font.render(f"Deaths: {self.dead_counter}", False, "#FFFFFF"), (screen_width-100, 130)) 
    