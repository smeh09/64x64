from .constants import CONSTANTS
from .utils import collide_and_move

import pygame, math

class Player:
    def __init__(self, position: pygame.Vector2):
        self.position = position
        self.velocity = pygame.Vector2(0, 0)
        
        # image stuff

        self.six_img = pygame.image.load('./assets/player_1_6.png').convert_alpha()
        self.four_img = pygame.image.load('./assets/player_1_4.png').convert_alpha()

        self.SIX_IMG_WIDTH = self.six_img.get_width()
        self.SIX_IMG_HEIGHT = self.six_img.get_height()
        self.FOUR_IMG_WIDTH = self.four_img.get_width()
        self.FOUR_IMG_HEIGHT = self.four_img.get_width()

        # rect stuff

        self.six_rect = pygame.FRect(self.position.x, self.position.y, self.SIX_IMG_WIDTH, self.SIX_IMG_HEIGHT)
        self.four_rect = pygame.FRect(self.get_four_x(self.position.x, False), self.position.y, self.four_img.get_width(), self.four_img.get_height())

        # movement stuff
        self.moving_left = False
        self.moving_right = False
        self.air_timer = 0
        self.old_collision_data = {'left': False, 'right': False, 'top': False, 'bottom': False, 'left_ramp_bottom': False, 'right_ramp_bottom': False}

        # direction stuff
        self.flipped = False # False -> right, True -> left

        # rotation
        self.four_rotation = 0

        # sword stuff
        self.attacking_sword = False
        self.swing_down_complete = False

        # trident stuff
        self.trident_mode_on = False
        self.trident_velocity = pygame.Vector2(0, 0)
        self.rotated_four_trident_img = self.four_img

        # health stuff
        self.health = 100

    def get_four_x(self, x, flipped):
        if not flipped:
            return x + self.SIX_IMG_WIDTH + 1
        else:
            return x - 1 - self.FOUR_IMG_WIDTH
    
    def get_six_x(self, x, flipped):
        if not flipped:
            return x - self.SIX_IMG_WIDTH - 1
        else:
            return x + self.FOUR_IMG_WIDTH + 1
    
    def attack_sword(self):
        if not self.attacking_sword and not self.trident_mode_on:
            self.attacking_sword = True
            self.four_rotation = 0
            self.swing_down_complete = False

    def reset_sword(self):
        self.attacking_sword = False
        self.four_rotation = 0
        self.swing_down_complete = False

    def attack_trident(self, trident_sfx):
        if not self.trident_mode_on and pygame.Vector2((self.four_rect.x - self.six_rect.x), (self.four_rect.y - self.six_rect.y)).length_squared() < 70.0:
            trident_sfx.play()
            self.trident_mode_on = True

    def render(self, display, colliders, mouse_coordinates, dt):

        mouse_x_direction = mouse_coordinates.x - self.six_rect.x
        if mouse_x_direction > 0:
            self.flipped = False
        elif mouse_x_direction < 0:
            self.flipped = True

        # horizontal movement
        if self.moving_left:
            self.velocity.x = pygame.math.lerp(self.velocity.x, -CONSTANTS['PLAYER_SPEED'], CONSTANTS['PLAYER_ACCELERATING_STEP'] * dt)

        if self.moving_right:
            self.velocity.x = pygame.math.lerp(self.velocity.x, CONSTANTS['PLAYER_SPEED'], CONSTANTS['PLAYER_ACCELERATING_STEP'] * dt)
        if not self.moving_left and not self.moving_right:
            self.velocity.x = pygame.math.lerp(self.velocity.x, 0, CONSTANTS['PLAYER_RETARDATION_STEP'] * dt)

        self.velocity.y += CONSTANTS['GRAVITY'] * dt
        if self.velocity.y > 250:
            self.velocity.y = 250

        if self.six_rect.x <= 0 or self.six_rect.x >= CONSTANTS['RESOLUTION_X'] - self.SIX_IMG_WIDTH:
            self.velocity.x *= -2

        six_rect_new_movement, collision_data_six = collide_and_move(self.six_rect, self.velocity * dt, colliders)
        
        rotated_four_img = pygame.transform.flip(pygame.transform.rotate(self.four_img, 360 - self.four_rotation), self.flipped, False)
        x_offset = rotated_four_img.get_width() - self.FOUR_IMG_WIDTH
        self.four_rect.width = rotated_four_img.get_width()
        self.four_rect.height = rotated_four_img.get_height()

        self.six_rect = six_rect_new_movement
        if not self.trident_mode_on:
            if self.flipped:
                self.four_rect.x = self.get_four_x(self.six_rect.x, self.flipped) - x_offset
            else:
                self.four_rect.x = self.get_four_x(self.six_rect.x, self.flipped)
            self.four_rect.y = self.six_rect.y
        collision_data = collision_data_six
        
        self.old_collision_data = collision_data
        if collision_data['bottom']:
            self.velocity.y = 0
            self.air_timer = 0
        else:
            self.air_timer += dt
            
        # sword attacking stuff
        if self.attacking_sword:
            if not self.swing_down_complete:
                self.four_rotation += CONSTANTS['SWING_DOWN_SPEED'] * dt
            else:
                self.four_rotation -= CONSTANTS['SWING_UP_SPEED'] * dt
            
            if self.four_rotation >= 180:
                self.swing_down_complete = True

            if self.four_rotation <= 0 and self.swing_down_complete:
                self.reset_sword()
                
        # trident attack stuff
        if self.trident_mode_on and self.trident_velocity.length_squared() == 0:

            for collider in colliders['left_ramp']:
                if self.four_rect.colliderect(collider) and self.flipped == True:
                    self.flipped = False
            for collider in colliders['right_ramp']:
                if self.four_rect.colliderect(collider) and self.flipped == False:
                    self.flipped = True
            
            if self.flipped:
                self.four_rect.x = self.get_four_x(self.six_rect.x, self.flipped) - x_offset
            else:
                self.four_rect.x = self.get_four_x(self.six_rect.x, self.flipped)
            
            uy = math.sqrt(2 * CONSTANTS['GRAVITY'] * abs(self.four_rect.y - mouse_coordinates.y))

            if uy:
                ux = CONSTANTS['GRAVITY'] * (mouse_coordinates.x - self.four_rect.x) / uy
            else:
                ux = ((mouse_coordinates.x - self.four_rect.x) / abs(mouse_coordinates.x - self.four_rect.x) ) * CONSTANTS['MAX_TRIDENT_SPEED_LIMIT']

            if abs(ux) > CONSTANTS['MAX_TRIDENT_SPEED_LIMIT']:
                ux = ((mouse_coordinates.x - self.four_rect.x) / abs(mouse_coordinates.x - self.four_rect.x) ) * CONSTANTS['MAX_TRIDENT_SPEED_LIMIT']

            self.trident_velocity.x = ux
            self.trident_velocity.y = -uy

        elif self.trident_mode_on and self.trident_velocity.length_squared() > 0:
            self.trident_velocity.y += CONSTANTS['GRAVITY'] * dt

        if self.trident_mode_on:
            theta = math.degrees(math.atan2(-self.trident_velocity.y, self.trident_velocity.x))
            self.rotated_four_trident_img = pygame.transform.rotate(self.four_img, theta - 90)
            self.four_rect, collision_data = collide_and_move(self.four_rect, self.trident_velocity * dt, colliders)
            if collision_data['left'] or collision_data['right'] or collision_data['bottom'] or collision_data['top'] or self.four_rect.y > 180:
                self.trident_velocity.x, self.trident_velocity.y = 0, 0
                self.trident_mode_on = False
        
        # rendering stuff
        display.blit(self.six_img, (self.six_rect.x, self.six_rect.y))

        if not self.trident_mode_on:

            self.four_rect.width = rotated_four_img.get_width()
            self.four_rect.height = rotated_four_img.get_height()

            if self.flipped:
                display.blit(rotated_four_img, (self.four_rect.x, self.four_rect.y))
            else:
                display.blit(rotated_four_img, (self.four_rect.x, self.four_rect.y))
        
        else:
            self.four_rect.width = self.rotated_four_trident_img.get_width()
            self.four_rect.height = self.rotated_four_trident_img.get_height()

            display.blit(self.rotated_four_trident_img, self.four_rect.topleft)