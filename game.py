from scripts.player import Player
from scripts.enemy import Enemy
from scripts.constants import CONSTANTS
from scripts.default_shaders import DEFAULT_VERTEX_SHADER, SCREEN_FRAGMENT_SHADER
from scripts.maps import selected_map

import pygame, sys, time, array, math, random
import moderngl as mgl
from pygame.locals import *

pygame.init()
clock = pygame.time.Clock()
pygame.mixer.pre_init(44100, -16, 2, 512)

monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]

SCREEN_SIZE = (CONSTANTS['WINDOW_WIDTH'], CONSTANTS['WINDOW_HEIGHT'])
screen = pygame.display.set_mode(monitor_size, pygame.OPENGL | pygame.DOUBLEBUF)
display = pygame.Surface((CONSTANTS['RESOLUTION_X'], CONSTANTS['RESOLUTION_Y']))
pygame.display.set_caption('64x64')

# colors
green = (148, 197, 172)
yellow = (255, 235, 153)

# screen VAO setup
ctx = mgl.create_context()
vbo = ctx.buffer(data=array.array('f', [
    -1.0, 1.0, 0.0, 1.0,
    1.0, 1.0, 1.0, 1.0,
    -1.0, -1.0, 0.0, 0.0,
    1.0, -1.0, 1.0, 0.0
]))
program = ctx.program(vertex_shader=DEFAULT_VERTEX_SHADER, fragment_shader=SCREEN_FRAGMENT_SHADER)
chromatic_strength = 5
program['chromatic_strength'] = chromatic_strength
vao = ctx.vertex_array(program, [(vbo, '2f 2f', 'in_vert', 'uvs')])
tex = ctx.texture((960, 540), 4)
tex.filter = (mgl.NEAREST, mgl.NEAREST)
tex.swizzle = 'BGRA'

# tileset initialization
tile_set = pygame.image.load('./assets/tileset.png').convert_alpha()
tile_config = {
    '0': (0, 0, 16, 16), #top left
    '1': (16, 0, 16, 16), #top middle
    '2': (32, 0, 16, 16), #top right
    '3': (0, 16, 16, 16), #left ramp
    '4': (16, 16, 16, 16), #middle
    '5': (32, 16, 16, 16), #right ramp
    '6': (0, 32, 16, 16), #left ramp connecter
    '7': (32, 32, 16, 16), #right ramp connecter
}

map = selected_map['maps'][selected_map['index']].split('\n')
map.pop(-1)
map.pop(0)

def render_tile(tile, coords):
    display.blit(tile_set, coords, area=pygame.Rect(*tile_config[tile]))

def render_map(map):
    colliders = {'normal': [], 'right_ramp': [], 'left_ramp': []}

    for y, row in enumerate(map):
        for x, tile in enumerate(row):
            if tile in tile_config.keys():
                tile_x = x * CONSTANTS['TILE_SIZE_X']
                tile_y = y * CONSTANTS['TILE_SIZE_Y']
                render_tile(tile, (tile_x, tile_y))

                if tile in ['1', '4', '7', '6']:
                    colliders['normal'].append(pygame.Rect(tile_x, tile_y, CONSTANTS['TILE_SIZE_X'], CONSTANTS['TILE_SIZE_Y']))
                if tile == '5':
                    colliders['right_ramp'].append(pygame.Rect(tile_x, tile_y, CONSTANTS['TILE_SIZE_X'], CONSTANTS['TILE_SIZE_Y']))
                if tile == '3':
                    colliders['left_ramp'].append(pygame.Rect(tile_x, tile_y, CONSTANTS['TILE_SIZE_X'], CONSTANTS['TILE_SIZE_Y']))

    return colliders

# sfx
hit_sfx = pygame.mixer.Sound('./assets/enemy_hit.wav')
jump_sfx = pygame.mixer.Sound('./assets/jump.wav')
trident_sfx = pygame.mixer.Sound('./assets/trident.wav')
dash_sfx = pygame.mixer.Sound('./assets/dash.wav')

hit_sfx.set_volume(0.4)
jump_sfx.set_volume(0.4)
trident_sfx.set_volume(0.4)
dash_sfx.set_volume(0.2)

# music
pygame.mixer.music.load('./assets/64_music.wav')
pygame.mixer.music.set_volume(1.2)
pygame.mixer.music.play(-1)

# initialize player
player_spawn_position = pygame.Vector2(50, 50)
enemy_spawn_position = pygame.Vector2(300, 50)

if selected_map['index'] == 4:
    player_spawn_position.x = 125
    enemy_spawn_position.x = 205

player = Player(player_spawn_position)

# initialize enemy
enemy = Enemy(enemy_spawn_position, trident_sfx)

# health image
health_bar_img = pygame.image.load('./assets/health_bar.png').convert_alpha()
health_img = pygame.image.load('./assets/health.png').convert_alpha()
enemy_health_img = pygame.image.load('./assets/enemy_health.png').convert_alpha()

# player indicator image
player_indicator_img = pygame.image.load('./assets/player_indicator.png').convert_alpha()

# cursor image
cursor = pygame.image.load('./assets/cursor.png').convert_alpha()

# dash timer images
dash_timer_img = pygame.image.load('./assets/dash_timer.png').convert_alpha()
dash_timer_container_img = pygame.image.load('./assets/dash_timer_container.png').convert_alpha()

# background images
background_layer_1 = pygame.image.load('./assets/bg_layer_1.png').convert_alpha()
background_layer_2 = pygame.image.load('./assets/bg_layer_2.png').convert_alpha()
background_layer_3 = pygame.image.load('./assets/bg_layer_3.png').convert_alpha()

# score
score = [0, 0]

# menu system
game_scenes = ['game', 'difficulty_choose', 'menu', 'pause']
current_scene = 2

# font setup
font = pygame.font.Font('./assets/Font.ttf', 16)

win_text = font.render('You Win!', False, green, None)
win_text_rect = win_text.get_rect()
win_text_rect.center = (CONSTANTS['RESOLUTION_X']/2, 70)

lose_text = font.render('You Lose!', False, green, None)
lose_text_rect = lose_text.get_rect()
lose_text_rect.center = (CONSTANTS['RESOLUTION_X']/2, 70)

play_again_text = font.render('Press R to play again', False, yellow, None)
play_again_text_rect = play_again_text.get_rect()
play_again_text_rect.center = (CONSTANTS['RESOLUTION_X']/2, 112)

# main menu text
title_font = pygame.font.Font('./assets/Font.ttf', 32)

game_name_text = title_font.render('64x64', False, yellow, None)
game_name_text_rect = game_name_text.get_rect()
GAME_NAME_TEXT_POSITION = (CONSTANTS['RESOLUTION_X']/2, CONSTANTS['RESOLUTION_Y']/2 - 30)
game_name_text_rect.center = GAME_NAME_TEXT_POSITION

game_start_text = font.render('Press S to start the game', False, green, None)
game_start_text_rect = game_start_text.get_rect()
GAME_START_TEXT_POSITION = (CONSTANTS['RESOLUTION_X']/2, CONSTANTS['RESOLUTION_Y']/2)
game_start_text_rect.center = GAME_START_TEXT_POSITION

game_dev_text = font.render('Made by @smeh09 [discord]', False, green, None)
game_dev_text_rect = game_dev_text.get_rect()
GAME_DEV_TEXT_POSITION = (CONSTANTS['RESOLUTION_X']/2, CONSTANTS['RESOLUTION_Y']/2 + 60)
game_dev_text_rect.centerx = GAME_DEV_TEXT_POSITION[0]
game_dev_text_rect.centery = GAME_DEV_TEXT_POSITION[1]

extreme_difficulty_text = font.render('Press X to play on extreme difficulty', False, yellow, None)
extreme_difficulty_text_rect = extreme_difficulty_text.get_rect()
INITIAL_EXTREME_DIFFICULTY_TEXT_CENTER = (CONSTANTS['RESOLUTION_X']/2, CONSTANTS['RESOLUTION_Y'] - 40)
extreme_difficulty_text_rect.center = INITIAL_EXTREME_DIFFICULTY_TEXT_CENTER

escape_text = font.render('Press "x key" to go back to menu', False, green, None)
escape_text_rect = escape_text.get_rect()
escape_text_rect.center = (CONSTANTS['RESOLUTION_X']/2, CONSTANTS['RESOLUTION_Y'] - 30)

game_paused_text = font.render('Game paused', False, yellow, None)
game_paused_text_rect = game_paused_text.get_rect()
game_paused_text_rect.center = (CONSTANTS['RESOLUTION_X']/2, 50)

resume_text = font.render('Press SPACE to resume the game', False, green, None)
resume_text_rect = resume_text.get_rect()
resume_text_rect.center = (CONSTANTS['RESOLUTION_X']/2, 100)

# difficulty cards
easy_card = pygame.image.load('./assets/easy_card.png').convert_alpha()
easy_card_rect = easy_card.get_rect()
easy_card_rect.left = 20
medium_card = pygame.image.load('./assets/medium_card.png').convert_alpha()
medium_card_rect = medium_card.get_rect()
medium_card_rect.left = 20 + easy_card.get_width() + 20
hard_card = pygame.image.load('./assets/hard_card.png').convert_alpha()
hard_card_rect = hard_card.get_rect()
hard_card_rect.left = medium_card_rect.left + medium_card.get_width() + 20

easy_card_rect.centery = medium_card_rect.centery = hard_card_rect.centery = CONSTANTS['RESOLUTION_Y']/2

# difficulty
difficulty_level = 3 # 0 -> EASY, 1 -> MEDIUM, 2 -> HARD, 3 -> V HARD, more like impossible xD

# dash
dash_timer = 0

# game over
game_over = False
game_over_status = ''

# hide mouse
pygame.mouse.set_visible(False)

# mouse Rect init
mouse_rect = pygame.Rect(0, 0, 1, 1)

# screenshake
screen_shake = 0

# particles
particles = []

def add_particles(position, quantity, size_range, velocity_x_range, velocity_y_range, color, life_time_range, enable_gravity=False):
    max_size = random.randint(size_range[0], size_range[1])
    for i in range(quantity):
        particle = {
            'position': pygame.Vector2(position.x, position.y),
            'size': max_size,
            'max_size': max_size,
            'velocity': pygame.Vector2(
                random.randint(velocity_x_range[0], velocity_x_range[1]),
                random.randint(velocity_y_range[0], velocity_y_range[1]),
            ),
            'color': color,
            'max_life_time': random.randint(life_time_range[0] * 10, life_time_range[1] * 10) / 10,
            'life_time': 0,
            'enable_gravity': enable_gravity
        }
        particles.append(particle)

# initialize time
t = 0
last_time = time.time()

while True:

    dt = pygame.math.clamp(time.time() - last_time, 0.00001, 0.99999)
    last_time = time.time()
    t += dt

    display.fill((27, 30, 52))
    ctx.clear(0, 0, 0)

    # first draw background
    background_layer_2.set_alpha(225 * (1/3))
    background_layer_3.set_alpha(225 * (5/6))

    display.blit(background_layer_1, (0, 0))
    display.blit(background_layer_2, (math.cos((t + 2) * 0.2) * 20.0, -math.sin((t + 2) * 0.5) * 15.0))
    display.blit(background_layer_3, (math.cos(t * 0.7) * 20.0, -math.sin(t * 0.9) * 15.0))

    # mouse coordinates
    mouse_coordinates = pygame.Vector2(*pygame.mouse.get_pos())
    mouse_coordinates /= CONSTANTS['SCALE']

    mouse_rect.center = mouse_coordinates

    if current_scene == 0:

        if game_over:
            chromatic_strength = 10 + math.sin(t) * 5.0

            # text
            score_text = font.render(f'{score[0]} : {score[1]}', False, yellow, None)
            score_text_rect = score_text.get_rect()
            score_text_rect.center = (CONSTANTS['RESOLUTION_X']/2, 20)

            display.blit(score_text, score_text_rect)

            if game_over_status == 'lose':
                display.blit(lose_text, lose_text_rect)
            else:
                display.blit(win_text, win_text_rect)
            display.blit(play_again_text, play_again_text_rect)
            display.blit(escape_text, escape_text_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                    pygame.quit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game_over = False

                        pygame.mixer.music.set_volume(1.2)

                        # reset stuff
                        
                        # choose a new map
                        i = random.randint(0, len(selected_map['maps']) - 1)
                        selected_map['index'] = i

                        # get formatted map
                        map = selected_map['maps'][selected_map['index']].split('\n')
                        map.pop(-1)
                        map.pop(0)

                        # spawn positions
                        player_spawn_position = pygame.Vector2(50, 50)
                        enemy_spawn_position = pygame.Vector2(300, 50)

                        if selected_map['index'] == 4:
                            player_spawn_position.x = 125
                            enemy_spawn_position.x = 205

                        player.six_rect.topleft = player_spawn_position
                        enemy.six_rect.topleft = enemy_spawn_position

                        # reset velocities and movement
                        player.moving_right = False
                        player.moving_left = False
                        enemy.movement_state = 'idle'
                        player.velocity, enemy.velocity = pygame.Vector2(0, 0), pygame.Vector2(0, 0)

                        # reset health
                        player.health = 100
                        enemy.health = 100

                        # reset trident position
                        player.trident_mode_on = False
                        player.four_rect.x = player.get_four_x(player.six_rect.x, player.flipped)
                        player.four_rect.y = player.six_rect.y
                        enemy.trident_mode_on = False
                        enemy.four_rect.x = player.get_four_x(enemy.six_rect.x, enemy.flipped)
                        enemy.four_rect.y = enemy.six_rect.y

                    if event.key == pygame.K_x:
                        current_scene = 2

                        # reset stuff

                        # choose a new map
                        i = random.randint(0, len(selected_map['maps']) - 1)
                        selected_map['index'] = i

                        # get formatted map
                        map = selected_map['maps'][selected_map['index']].split('\n')
                        map.pop(-1)
                        map.pop(0)

                        # spawn positions
                        player_spawn_position = pygame.Vector2(50, 50)
                        enemy_spawn_position = pygame.Vector2(300, 50)

                        if selected_map['index'] == 4:
                            player_spawn_position.x = 125
                            enemy_spawn_position.x = 205

                        player.six_rect.topleft = player_spawn_position
                        enemy.six_rect.topleft = enemy_spawn_position

                        # reset velocities and movement
                        player.moving_right = False
                        player.moving_left = False
                        enemy.movement_state = 'idle'
                        player.velocity, enemy.velocity = pygame.Vector2(0, 0), pygame.Vector2(0, 0)

                        # reset health
                        player.health = 100
                        enemy.health = 100

                        # reset trident position
                        player.trident_mode_on = False
                        player.four_rect.x = player.get_four_x(player.six_rect.x, player.flipped)
                        player.four_rect.y = player.six_rect.y
                        enemy.trident_mode_on = False
                        enemy.four_rect.x = player.get_four_x(enemy.six_rect.x, enemy.flipped)
                        enemy.four_rect.y = enemy.six_rect.y
        else:
            chromatic_strength = 5

            # draw map
            colliders = render_map(map)

            # draw player
            player.render(display, colliders, mouse_coordinates, dt)

            # draw enemy
            damage = enemy.render(display, colliders, selected_map['index'], player, difficulty_level, t, dt)

            if damage['player']:
                player.health = max(player.health - damage['player'], 0)
                if enemy.trident_mode_on:
                    enemy.trident_velocity.x, enemy.trident_velocity.y = 0, 0
                    enemy.trident_mode_on = False

                    relative_trident_position = enemy.four_rect.x - player.six_rect.x
                    if relative_trident_position > 0:
                        # hit from right
                        add_particles(
                            pygame.Vector2(player.six_rect.right, player.six_rect.centery), #position
                            25, #quantity
                            [2, 5], #size range
                            [-5, 25], #velocity x range
                            [-200, 10], #velocity y range
                            [217, 98, 107], #color,
                            [0.2, 0.4]
                        )
                    else:
                        # hit from left
                        add_particles(
                            pygame.Vector2(player.six_rect.left, player.six_rect.centery), #position
                            25, #quantity
                            [2, 5], #size range
                            [-25, 5], #velocity x range
                            [-200, 10], #velocity y range
                            [217, 98, 107], #color
                            [0.2, 0.6]
                        )
                else:
                    # damaged by enemy's sword
                    if enemy.flipped == True: #enemy facing towards left, player hurt on right side
                        add_particles(
                            pygame.Vector2(player.six_rect.right, player.six_rect.centery), #position
                            25, #quantity
                            [2, 5], #size range
                            [-5, 25], #velocity x range
                            [-200, 10], #velocity y range
                            [217, 98, 107], #color
                            [0.2, 0.6]
                        )
                    else:
                        add_particles(
                            pygame.Vector2(player.six_rect.left, player.six_rect.centery), #position
                            25, #quantity
                            [2, 5], #size range
                            [-25, 5], #velocity x range
                            [-200, 10], #velocity y range
                            [217, 98, 107], #color
                            [0.2, 0.6]
                        )
                hit_sfx.play()
                screen_shake = 0.2
            
            if damage['enemy']:
                enemy.health = max(enemy.health - damage['enemy'], 0)
                if player.trident_mode_on:
                    player.trident_velocity.x, player.trident_velocity.y = 0, 0
                    player.trident_mode_on = False
                    
                    relative_trident_position = player.four_rect.x - enemy.six_rect.x
                    if relative_trident_position > 0:
                        # hit from right
                        add_particles(
                            pygame.Vector2(enemy.six_rect.right, enemy.six_rect.centery), #position
                            25, #quantity
                            [2, 5], #size range
                            [-5, 25], #velocity x range
                            [-200, 10], #velocity y range
                            [217, 98, 107], #color,
                            [0.2, 0.4],
                            enable_gravity=False
                        )
                    else:
                        # hit from left
                        add_particles(
                            pygame.Vector2(enemy.six_rect.left, enemy.six_rect.centery), #position
                            25, #quantity
                            [2, 5], #size range
                            [-25, 5], #velocity x range
                            [-200, 10], #velocity y range
                            [217, 98, 107], #color
                            [0.2, 0.6],
                            enable_gravity=False
                        )
                else:
                    if player.flipped == True:
                        add_particles(
                            pygame.Vector2(enemy.six_rect.right, enemy.six_rect.centery), #position
                            25, #quantity
                            [2, 5], #size range
                            [-5, 25], #velocity x range
                            [-200, 10], #velocity y range
                            [217, 98, 107], #color
                            [0.2, 0.6]
                        )
                    else:
                        add_particles(
                            pygame.Vector2(enemy.six_rect.left, enemy.six_rect.centery), #position
                            25, #quantity
                            [2, 5], #size range
                            [-25, 5], #velocity x range
                            [-200, 10], #velocity y range
                            [217, 98, 107], #color
                            [0.2, 0.6]
                        )
                hit_sfx.play()
                screen_shake = 0.2

            if player.six_rect.y > CONSTANTS['RESOLUTION_Y']:
                player.health = 0

            if enemy.six_rect.y > CONSTANTS['RESOLUTION_Y']:
                enemy.health = 0

            if player.health == 0:
                score[1] += 1
                game_over_status = 'lose'
                game_over = True
                pygame.mixer.music.set_volume(0.5)
                particles = []
            if enemy.health == 0:
                score[0] += 1
                game_over_status = 'win'
                game_over = True
                pygame.mixer.music.set_volume(0.5)
                particles = []

            # draw health UI
            health_img_width = (player.health)/100 * (health_img.get_width())
            display.blit(health_img, (player.six_rect.x - 2, player.six_rect.y - 12 + math.sin(t * 3.0) * 5.0), area=pygame.Rect(0, 0, health_img_width, 2))
            display.blit(health_bar_img, (player.six_rect.x - 7, player.six_rect.y - 14 + math.sin(t * 3.0) * 5.0))

            enemy_health_img_width = (enemy.health)/100 * (enemy_health_img.get_width())
            display.blit(enemy_health_img, (enemy.six_rect.x - 2, enemy.six_rect.y - 12 + math.sin(t * 3.0 + 3.0) * 5.0), area=pygame.Rect(0, 0, enemy_health_img_width, 2))
            display.blit(health_bar_img, (enemy.six_rect.x - 7, enemy.six_rect.y - 14 + math.sin(t * 3.0 + 3.0) * 5.0))

            # dash timer image
            dash_img_width = (t - dash_timer)/0.7 * (dash_timer_img.get_width())
            display.blit(dash_timer_container_img, (20, 20))
            display.blit(dash_timer_img, (20 + 18, 20 + 6), pygame.Rect(0, 0, dash_img_width, dash_timer_img.get_height()))

            # draw player indicator
            display.blit(player_indicator_img, (player.six_rect.x + player.SIX_IMG_WIDTH/4, player.six_rect.y - 35 + math.sin((t * 2.0) * 3.0) * 10.0))

            # update particles
            removal_particle_indices = []
            for i, particle in enumerate(particles):
                if particle['enable_gravity']:
                    particle['velocity'].y += CONSTANTS['GRAVITY'] * dt

                particle['position'].x += particle['velocity'].x * dt
                particle['position'].y += particle['velocity'].y * dt
                
                pygame.draw.circle(display, particle['color'], particle['position'], particle['size'])
                
                particle['life_time'] += dt
                particle['size'] = ((particle['max_life_time'] - particle['life_time']) / particle['max_life_time']) * particle['max_size']

                if particle['size'] <= 0:
                    removal_particle_indices.append(i)

            removal_particle_indices.sort(reverse=True)

            for removal_particle_index in removal_particle_indices:
                particles.pop(removal_particle_index)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                    pygame.quit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d:
                        player.moving_right = True
                    if event.key == pygame.K_a:
                        player.moving_left = True
                    if event.key == pygame.K_SPACE and player.air_timer <= 0.13:
                        player.velocity.y = -250
                        jump_sfx.play()
                    if event.key == pygame.K_e and t - dash_timer >= 0.7:
                        if player.moving_left:
                            player_dirn = -1
                            add_particles(
                                pygame.Vector2(player.six_rect.left, player.six_rect.centery),
                                30,
                                [3, 7],
                                [10, 100],
                                [0, 100], 
                                yellow,
                                [0.2, 1.0],
                                enable_gravity=False
                            )
                        elif player.moving_right:
                            player_dirn = 1
                            add_particles(
                                pygame.Vector2(player.six_rect.right, player.six_rect.centery),
                                30,
                                [3, 7],
                                [-100, 10],
                                [0, 100], 
                                yellow,
                                [0.2, 1.0],
                                enable_gravity=False
                            )
                        else:
                            if player.flipped:
                                player_dirn = -1
                            else:
                                player_dirn = 1
                        player.velocity.x = (CONSTANTS['DASH_SPEED'] * player_dirn)
                        dash_sfx.play()
                        dash_timer = t
                    if event.key == pygame.K_ESCAPE:
                        current_scene = 3

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_d:
                        player.moving_right = False
                    if event.key == pygame.K_a:
                        player.moving_left = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    player.attack_sword()
                elif event.button == 1:
                    player.attack_trident(trident_sfx)

    elif current_scene == 3:
        # GAME PAUSE SCENE
        score_text = font.render(f'{score[0]} : {score[1]}', False, yellow, None)
        score_text_rect = score_text.get_rect()
        score_text_rect.center = (CONSTANTS['RESOLUTION_X']/2, 20)

        display.blit(score_text, score_text_rect)
        display.blit(game_paused_text, game_paused_text_rect)
        display.blit(resume_text, resume_text_rect)
        display.blit(escape_text, escape_text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                pygame.quit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    current_scene = 2

                    # reset stuff

                    # choose a new map
                    i = random.randint(0, len(selected_map['maps']) - 1)
                    selected_map['index'] = i

                    # get formatted map
                    map = selected_map['maps'][selected_map['index']].split('\n')
                    map.pop(-1)
                    map.pop(0)

                    # spawn positions
                    player_spawn_position = pygame.Vector2(50, 50)
                    enemy_spawn_position = pygame.Vector2(300, 50)

                    if selected_map['index'] == 4:
                        player_spawn_position.x = 125
                        enemy_spawn_position.x = 205

                    player.six_rect.topleft = player_spawn_position
                    enemy.six_rect.topleft = enemy_spawn_position

                    # reset velocities and movement
                    player.moving_right = False
                    player.moving_left = False
                    enemy.movement_state = 'idle'
                    player.velocity, enemy.velocity = pygame.Vector2(0, 0), pygame.Vector2(0, 0)

                    # reset health
                    player.health = 100
                    enemy.health = 100

                    # reset trident position
                    player.trident_mode_on = False
                    player.four_rect.x = player.get_four_x(player.six_rect.x, player.flipped)
                    player.four_rect.y = player.six_rect.y
                    enemy.trident_mode_on = False
                    enemy.four_rect.x = player.get_four_x(enemy.six_rect.x, enemy.flipped)
                    enemy.four_rect.y = enemy.six_rect.y
            
                if event.key == pygame.K_SPACE:
                    current_scene = 0

    elif current_scene == 1:
        # DIFFICULTY CHOOSING SCENE

        chromatic_strength = 5 + math.sin(t) * 3.0

        extreme_difficulty_text_rect.y = INITIAL_EXTREME_DIFFICULTY_TEXT_CENTER[1] + math.sin(t * 3.0) * 5.0

        display.blit(easy_card, easy_card_rect.topleft)
        display.blit(medium_card, medium_card_rect.topleft)
        display.blit(hard_card, hard_card_rect.topleft)
        display.blit(extreme_difficulty_text, extreme_difficulty_text_rect)

        mouse_down = pygame.mouse.get_pressed()[0]

        if mouse_rect.colliderect(easy_card_rect):
            easy_card_rect.centery = CONSTANTS['RESOLUTION_Y']/2 - 10
            if mouse_down:
                trident_sfx.play()
                difficulty_level = 0
                current_scene = 0
        else:
            easy_card_rect.centery = CONSTANTS['RESOLUTION_Y']/2

        if mouse_rect.colliderect(medium_card_rect):
            medium_card_rect.centery = CONSTANTS['RESOLUTION_Y']/2 - 10
            if mouse_down:
                trident_sfx.play()
                difficulty_level = 1
                current_scene = 0
        else:
            medium_card_rect.centery = CONSTANTS['RESOLUTION_Y']/2

        if mouse_rect.colliderect(hard_card_rect):
            hard_card_rect.centery = CONSTANTS['RESOLUTION_Y']/2 - 10
            if mouse_down:
                trident_sfx.play()
                difficulty_level = 2
                current_scene = 0
        else:
            hard_card_rect.centery = CONSTANTS['RESOLUTION_Y']/2

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    difficulty_level = 3
                    current_scene = 0

    elif current_scene == 2:
        # MAIN MENU

        chromatic_strength = 10 + math.sin(t)

        game_name_text_rect.centery = GAME_NAME_TEXT_POSITION[1] + math.sin(t * 3.0) * 7.0
        game_start_text_rect.centery = GAME_START_TEXT_POSITION[1] + math.sin(t * 3.0) * 7.0

        display.blit(game_name_text, game_name_text_rect)
        display.blit(game_start_text, game_start_text_rect)
        display.blit(game_dev_text, game_dev_text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                pygame.quit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    trident_sfx.play()
                    current_scene = 1

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    # last render - cursor
    display.blit(cursor, (mouse_coordinates.x - cursor.get_width()/2, mouse_coordinates.y - cursor.get_height()/2))

    if screen_shake > 0.0:
        screen_shake -= dt

    if screen_shake <= 0:
        screen_shake = 0
    
    render_offset = [0, 0]
    if screen_shake:
        render_offset[0] = (random.randint(0, 8) - 4)/200
        render_offset[1] = (random.randint(0, 8) - 4)/200

    program['render_offset'] = (render_offset[0], render_offset[1])

    scaled_up_display = pygame.transform.flip(pygame.transform.scale(display, SCREEN_SIZE), False, True)

    tex.write(scaled_up_display.get_view('2'))
    tex.use(0)
    program['tex'] = 0
    program['chromatic_strength'] = chromatic_strength
    vao.render(mode=mgl.TRIANGLE_STRIP)

    pygame.display.flip()
    #clock.tick(60)