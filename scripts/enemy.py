from .constants import CONSTANTS
from .utils import collide_and_move

import pygame, math, random

class Enemy:
    def __init__(self, position: pygame.Vector2, trident_sfx):
        self.position = position
        self.velocity = pygame.Vector2(0, 0)

        self.trident_sfx = trident_sfx

        self.six_img = pygame.image.load('./assets/player_2_6.png').convert_alpha()
        self.four_img = pygame.image.load('./assets/player_2_4.png').convert_alpha()

        self.SIX_IMG_WIDTH = self.six_img.get_width()
        self.SIX_IMG_HEIGHT = self.six_img.get_height()
        self.FOUR_IMG_WIDTH = self.four_img.get_width()
        self.FOUR_IMG_HEIGHT = self.four_img.get_width()

        # rect stuff

        self.six_rect = pygame.FRect(self.position.x, self.position.y, self.SIX_IMG_WIDTH, self.SIX_IMG_HEIGHT)
        self.four_rect = pygame.FRect(self.get_four_x(self.position.x, False), self.position.y, self.four_img.get_width(), self.four_img.get_height())

        # movement stuff
        self.old_collision_data = {'left': False, 'right': False, 'top': False, 'bottom': False, 'left_ramp_bottom': False, 'right_ramp_bottom': False}

        # direction stuff
        self.flipped = False # False -> right, True -> left

        # sword stuff
        self.attacking_sword = False
        self.four_rotation = 0
        self.swing_down_complete = False
        
        # trident stuff
        self.trident_mode_on = False
        self.trident_velocity = pygame.Vector2(0, 0)
        self.rotated_four_trident_img = self.four_img

        # health stuff
        self.health = 100
        self.last_frame_gave_damage_from_sword = False
        self.last_frame_took_damage_from_sword = False
        self.last_frame_gave_damage_from_trident = False
        self.last_frame_took_damage_from_trident = False

        # enemy logic
        self.movement_state = 'idle'
        self.old_collision_data_six = {'left': False, 'right': False, 'top': False, 'bottom': False, 'left_ramp_bottom': False, 'right_ramp_bottom': False}
        self.flee_reverse = False
        self.before_flee_reverse_direction = 1

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
        if not self.attacking_sword:
            self.attacking_sword = True
            self.four_rotation = 0
            self.swing_down_complete = False

    def reset_sword(self):
        self.attacking_sword = False
        self.four_rotation = 0
        self.swing_down_complete = False

    def attack_trident(self):
        if not self.trident_mode_on and pygame.Vector2((self.four_rect.x - self.six_rect.x), (self.four_rect.y - self.six_rect.y)).length_squared() <= 66.0:
            self.trident_sfx.play()
            self.trident_mode_on = True
    
    def render(self, display, colliders, map_index, player, difficulty_level, time, dt):

        # LOGIC
        distance_from_player = pygame.Vector2((player.six_rect.x - self.six_rect.x), (player.six_rect.y - self.six_rect.y)).length()

        # movement states -> IDLE, CHASING, FLEEING
        # IDLE - DISTANCE > SOME CONSTRANT
        # CHASING - ENEMY HEALTH - PLAYER HEALTH > -60 AND DISTANCE <= SOME CONSTRAINT
        # FLEEING - ENEMY - HEALTH - PLAYER HEALTH <= -60 AND DISTANCE <= SOME CONSTRAINT

        # CHASING
        player_relative_direction = player.six_rect.x - self.six_rect.x
        if player_relative_direction != 0:
            player_relative_direction /= abs(player_relative_direction)
        
        if player_relative_direction > 0:
            chasing_direction_multiplier = 1
            self.flipped = False
        else:
            chasing_direction_multiplier = -1
            self.flipped = True

        # CHASE
        enemy_idling_threshold = CONSTANTS['ENEMY_IDLING_THRESHOLD_DISTANCE'][difficulty_level]
        if map_index == 3:
            enemy_idling_threshold = 100
        if self.health - player.health > -60 and distance_from_player <= enemy_idling_threshold and distance_from_player >= 20:
            self.movement_state = 'chase'
            self.velocity.x = chasing_direction_multiplier * CONSTANTS['ENEMY_SPEED'][difficulty_level]
        
        # FLEE
        elif self.health - player.health <= -60 and distance_from_player <= enemy_idling_threshold:
            self.movement_state = 'flee'
            if not self.flee_reverse:
                self.velocity.x = -chasing_direction_multiplier * CONSTANTS['ENEMY_SPEED'][difficulty_level]
            else:
                self.velocity.x = chasing_direction_multiplier * CONSTANTS['ENEMY_SPEED'][difficulty_level]
                
                player_relative_direction = player.six_rect.x - self.six_rect.x
                if player_relative_direction != 0:
                    player_relative_direction /= abs(player_relative_direction)

                if abs(self.six_rect.x - 960/2) < 5.0:
                    self.flee_reverse = False
            
            if self.six_rect.x == 0 or self.six_rect.x == CONSTANTS['RESOLUTION_X'] - self.SIX_IMG_WIDTH:
                self.flee_reverse = True
                self.before_flee_reverse_direction = player_relative_direction
        
        # IDLE
        else:
            self.movement_state = 'idle'
            self.velocity.x = 0

        # JUMP
        if (self.movement_state == 'chase' or self.flee_reverse) and time % 1.7 < 0.1 and time >= 1.7 and self.old_collision_data['bottom']:
            self.velocity.y = -250

        
        # ATTACK

        # SWORD
        if distance_from_player <= 35 and time % CONSTANTS['ENEMY_SWORD_ATTACK_GAP'][difficulty_level] < 0.1 and time >= CONSTANTS['ENEMY_SWORD_ATTACK_GAP'][difficulty_level]:
            self.attack_sword()
        else:
            # TRIDENT
            if distance_from_player >= 35 and time % CONSTANTS['ENEMY_TRIDENT_ATTACK_GAP'][difficulty_level] < 0.1 and time >= CONSTANTS['ENEMY_TRIDENT_ATTACK_GAP'][difficulty_level] and self.old_collision_data_six['bottom']:
                self.velocity.x = 0
                self.attack_trident()
        
        # movement stuff
        self.velocity.y += CONSTANTS['GRAVITY'] * dt
        if self.velocity.y > 250:
            self.velocity.y = 250

        six_rect_new_movement, collision_data_six = collide_and_move(self.six_rect, self.velocity * dt, colliders)
        self.old_collision_data_six = collision_data_six
        
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

        # clamp positions
        if self.six_rect.x < 0:
            self.six_rect.x = 0
        if self.six_rect.x > CONSTANTS['RESOLUTION_X'] - self.SIX_IMG_WIDTH:
            self.six_rect.x = CONSTANTS['RESOLUTION_X'] - self.SIX_IMG_WIDTH

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
        if self.trident_mode_on and pygame.Vector2((self.four_rect.x - self.six_rect.x), (self.four_rect.y - self.six_rect.y)).length_squared() < 64.2:

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

            uy = math.sqrt(2 * CONSTANTS['GRAVITY'] * random.randint(75, 130))
            T = 2 * uy / CONSTANTS['GRAVITY']
            predicted_player_coordinate_x = player.six_rect.x + player.velocity.x * T + (self.SIX_IMG_WIDTH/2)
            wanna_predict = [True, True, False][random.randint(0, 2)]
            if map_index == 3:
                wanna_predict = False
            if player.six_rect.x <= 35.0 or player.six_rect.x >= (CONSTANTS['RESOLUTION_X'] - 35.0):
                wanna_predict = False
            if wanna_predict:
                final_coordinate = predicted_player_coordinate_x
            else:
                final_coordinate = player.six_rect.x
            ux = min(CONSTANTS['GRAVITY'] * (final_coordinate - self.four_rect.x) / (2 * uy), CONSTANTS['MAX_TRIDENT_SPEED_LIMIT'])

            self.trident_velocity.x = ux
            self.trident_velocity.y = -uy

        elif self.trident_mode_on and self.trident_velocity.length_squared() > 0:
            self.trident_velocity.y += CONSTANTS['GRAVITY'] * dt

        if self.trident_mode_on:
            theta = math.degrees(math.atan2(-self.trident_velocity.y, self.trident_velocity.x))
            self.rotated_four_trident_img = pygame.transform.rotate(self.four_img, theta - 90)
            self.four_rect, collision_data = collide_and_move(self.four_rect, self.trident_velocity * dt, colliders)
            if collision_data['left'] or collision_data['right'] or collision_data['bottom'] or collision_data['top'] or self.four_rect.y > CONSTANTS['RESOLUTION_Y']:
                self.trident_velocity.x, self.trident_velocity.y = 0, 0
                self.trident_mode_on = False

        if not self.trident_mode_on and pygame.Vector2((self.four_rect.x - self.six_rect.x), (self.four_rect.y - self.six_rect.y)).length_squared() <= 66.0:
            self.four_rect.x = self.get_four_x(self.six_rect.x, self.flipped)

        # collision stuff
        damage = {'player': 0, 'enemy': 0}
        
        if self.attacking_sword and not self.last_frame_gave_damage_from_sword:
            if player.six_rect.colliderect(self.four_rect):
                damage['player'] += 25
                self.last_frame_gave_damage_from_sword = True
        elif not self.attacking_sword:
            self.last_frame_gave_damage_from_sword = False
        
        if self.trident_mode_on and not self.last_frame_gave_damage_from_trident:
            if player.six_rect.colliderect(self.four_rect):
                damage['player'] += 17
                self.last_frame_gave_damage_from_trident = True
        elif not self.trident_mode_on:
            self.last_frame_gave_damage_from_trident = False
    

        if player.attacking_sword and not self.last_frame_took_damage_from_sword:
            if self.six_rect.colliderect(player.four_rect):
                damage['enemy'] += 25
                self.last_frame_took_damage_from_sword = True
        elif not player.attacking_sword:
                self.last_frame_took_damage_from_sword = False
        
        if player.trident_mode_on and not self.last_frame_took_damage_from_trident:
            if self.six_rect.colliderect(player.four_rect):
                damage['enemy'] += 17
                self.last_frame_took_damage_from_trident = True
        elif not player.trident_mode_on:
            self.last_frame_took_damage_from_trident = False

        # rendering stuff
        display.blit(self.six_img, (self.six_rect.x, self.six_rect.y))

        if not self.trident_mode_on:
            if self.flipped:
                display.blit(rotated_four_img, (self.four_rect.x, self.four_rect.y))
            else:
                display.blit(rotated_four_img, (self.four_rect.x, self.four_rect.y))
        
        else:
            self.four_rect.width = self.rotated_four_trident_img.get_width()
            self.four_rect.height = self.rotated_four_trident_img.get_height()

            display.blit(self.rotated_four_trident_img, self.four_rect.topleft)

        return damage