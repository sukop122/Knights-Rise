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
        self.max_charge = 16
        self.in_air = False
        self.speed = 3

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
        

    def update(self, keys, platforms, current_level):

    #respawn - only on level 0
        if self.y > screen_height + 200 and current_level == 2:
            self.respawn()


    #Jumping and Charging
        if self.on_ground:
            if keys[pg.K_SPACE]:
                self.charging = True
                self.vel_x = 0
                self.charge_power += 0.4
                self.state = "charge"
            
                if self.charging:    
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
                    
               

            elif self.charging:
                self.jump(self.charge_power)
                self.charging = False
                self.charge_power = 0
                
                
        
    # Movement Left and Right
        if self.on_ground and not self.charging and self.state != "charge":
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


    #Gravity
        gravity = 0.6
        self.vel_y += gravity

    #Aplication of velocities
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
                    if self.y >= screen_height - 50 - self.height:
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
        
        #################Collision with platforms#######################################################################################################
        self.x += self.vel_x
        self.y += self.vel_y

        self.rect.topleft = (self.x + self.hitbox_offset_x, self.y + self.hitbox_offset_y)

        landed = False
        for plat in platforms:
            next_rect = self.rect.move(0, self.vel_y)

            # horizontal overlap check
            horiz = (self.rect.right > plat.rect.left) and (self.rect.left < plat.rect.right)

            # Landing on top (moving down)
            tolerance = max(20, abs (self.vel_y) + 4)
            if self.vel_y > 0 and horiz:
                if self.rect.bottom <= plat.rect.top + tolerance and next_rect.bottom >= plat.rect.top:
                    self.y = plat.rect.top - self.hitbox_offset_y - self.hitbox_height
                    self.vel_y = 0
                    self.on_ground = True
                    self.in_air = False
                    self.collision = False
                    if not self.charging:
                        self.state = "idle" if self.vel_x == 0 else "run"
                    landed = True
                    break

            #Bump from bottom (head hit) - moving up (teacher)
            if (

                self.vel_y < 0 and
                self.rect.top >= plat.rect.bottom - tolerance and
                next_rect.top <= plat.rect.bottom and
                self.rect.right > plat.rect.left and
                self.rect.left < plat.rect.right and
                self.state != "bump"
                
            ):
                self.y = plat.rect.bottom - self.hitbox_offset_y + self.hitbox_height
                self.vel_y *= - 0.5
                self.state = "bump"
                
            ##Bump from bottom (head hit) - moving up (AI help)
            #if self.vel_y < 0 and horiz:
            #    tol = max(2, int(abs(self.vel_y)))
            #    if (self.rect.top >= plat.rect.bottom - tol) and (next_rect.top <= plat.rect.bottom + tol):
            #        # position player just below platform bottom
            #        self.y = plat.rect.bottom - self.hitbox_offset_y
            #        self.vel_y = 0.5
            #        self.state = "bump"
            #        # update rect to new position so horizontal checks use corrected position
            #        self.rect.topleft = (self.x + self.hitbox_offset_x, self.y + self.hitbox_offset_y)

            # Bump from left
            if self.vel_x > 0 and self.rect.right >= plat.rect.left and self.rect.left < plat.rect.left and self.rect.bottom > plat.rect.top + 10 and self.rect.top < plat.rect.bottom - 10:
                self.x = plat.rect.left - self.hitbox_offset_x - self.hitbox_width
                self.vel_x *= -0.5
                self.state = "bump"

            # Bump from right
            if self.vel_x < 0 and self.rect.left <= plat.rect.right and self.rect.right > plat.rect.right and self.rect.bottom > plat.rect.top + 10 and self.rect.top < plat.rect.bottom - 10:
                self.x = plat.rect.right - self.hitbox_offset_x
                self.vel_x *= -0.5
                self.state = "bump"
        if not landed and not self.charging:
                self.on_ground = False
                self.in_air = True
        
        self.rect.topleft = (self.x + self.hitbox_offset_x, self.y + self.hitbox_offset_y)

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
            frame = current_anim[int(self.index)% len(current_anim)]
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
    