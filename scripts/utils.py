import pygame

def get_collisions(rect, colliders):
    collisions = []
    for collider in colliders['normal']:
        if rect.colliderect(collider):
            collisions.append(collider)

    return collisions

def get_right_ramp_collisions(rect, colliders):
    right_ramp_collisions = []
    for ramp in colliders['right_ramp']:
        if rect.colliderect(ramp):
            right_ramp_collisions.append(ramp)
    return right_ramp_collisions

def get_left_ramp_collisions(rect, colliders):
    left_ramp_collisions = []
    for ramp in colliders['left_ramp']:
        if rect.colliderect(ramp):
            left_ramp_collisions.append(ramp)
    return left_ramp_collisions

def collide_and_move(rect: pygame.FRect, velocity, colliders):
    # normal collisions
    collision_data = {'left': False, 'right': False, 'top': False, 'bottom': False, 'left_ramp_bottom': False, 'right_ramp_bottom': False}

    rect.x += velocity.x
    collisions = get_collisions(rect, colliders)

    for collision in collisions:
        if velocity.x > 0:
            rect.right = collision.left
            collision_data['right'] = True
        if velocity.x < 0:
            rect.left = collision.right
            collision_data['left'] = True

    rect.y += velocity.y
    collisions = get_collisions(rect, colliders)

    for collision in collisions:
        if velocity.y < 0:
            rect.top = collision.bottom
            collision_data['top'] = True
        if velocity.y > 0:
            rect.bottom = collision.top
            collision_data['bottom'] = True

    # right ramp collisions
    right_ramp_collisions = get_right_ramp_collisions(rect, colliders)
    for ramp in right_ramp_collisions:
        relative_x = rect.right - ramp.left
        relative_y = ramp.bottom - rect.bottom
        destination_y = relative_x
        if relative_y <= destination_y + 5.0 and velocity.y >= 0:
            relative_y = destination_y
            rect.bottom = ramp.bottom - relative_y
            collision_data['right_ramp_bottom'] = collision_data['bottom'] = True

    # left ramp collisions
    left_ramp_collisions = get_left_ramp_collisions(rect, colliders)
    for ramp in left_ramp_collisions:
        relative_x = ramp.right - rect.left
        relative_y = ramp.bottom - rect.bottom
        destination_y = relative_x
        if relative_y <= destination_y + 5.0 and velocity.y >= 0:
            relative_y = destination_y
            rect.bottom = ramp.bottom - relative_y
            collision_data['left_ramp_bottom'] = collision_data['bottom'] = True
    
    return rect, collision_data