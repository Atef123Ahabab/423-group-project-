from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# Window and arena settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
ARENA_LIMIT = 600
fovY = 120

# Observer settings
observer_pos = [0, 450, 450]
observer_angle = 0
observer_height = 450
first_person_view = False

# Game status flags
game_running = True
auto_aim_on = False
cheat_vision_active = False

# Hero attributes
hero_pos = [0, 0, 0]
gun_angle = 0
player_speed = 12
rotation_speed = 6
lives_left = 5
score = 0

# Ammunition tracking
ammunition = []
shots_missed = 0
MAX_MISSES = 10
bullet_speed = 18
bullet_size = 8

# Target entities
targets = []
ENEMY_COUNT = 5
target_speed = 0.3
target_size = 40
enemy_scale = 1.0
scale_direction = 1

def draw_text(x_coord, y_coord, text_msg, font_style=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    gluOrtho2D(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x_coord, y_coord)
    for ch in text_msg:
        glutBitmapCharacter(font_style, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_arena_floor():
    tile_size = 100
    glBegin(GL_QUADS)
    
    for x_pos in range(-ARENA_LIMIT, ARENA_LIMIT + tile_size, tile_size):
        for y_pos in range(-ARENA_LIMIT, ARENA_LIMIT + tile_size, tile_size):
            tile_color = ((x_pos + y_pos) // tile_size) % 2
            if tile_color == 0:
                glColor3f(1.0, 1.0, 1.0)
            else:
                glColor3f(0.7, 0.5, 0.95)
            
            glVertex3f(x_pos, y_pos, 0)
            glVertex3f(x_pos + tile_size, y_pos, 0)
            glVertex3f(x_pos + tile_size, y_pos + tile_size, 0)
            glVertex3f(x_pos, y_pos + tile_size, 0)
    
    glEnd()
    
    barrier_height = 100
    glBegin(GL_QUADS)
    
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(-ARENA_LIMIT, -ARENA_LIMIT, 0)
    glVertex3f(-ARENA_LIMIT, ARENA_LIMIT + tile_size, 0)
    glVertex3f(-ARENA_LIMIT, ARENA_LIMIT + tile_size, barrier_height)
    glVertex3f(-ARENA_LIMIT, -ARENA_LIMIT, barrier_height)
    
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(ARENA_LIMIT + tile_size, -ARENA_LIMIT, 0)
    glVertex3f(ARENA_LIMIT + tile_size, ARENA_LIMIT + tile_size, 0)
    glVertex3f(ARENA_LIMIT + tile_size, ARENA_LIMIT + tile_size, barrier_height)
    glVertex3f(ARENA_LIMIT + tile_size, -ARENA_LIMIT, barrier_height)
    
    glColor3f(1.0, 1.0, 1.0)
    glVertex3f(-ARENA_LIMIT, ARENA_LIMIT + tile_size, 0)
    glVertex3f(ARENA_LIMIT + tile_size, ARENA_LIMIT + tile_size, 0)
    glVertex3f(ARENA_LIMIT + tile_size, ARENA_LIMIT + tile_size, barrier_height)
    glVertex3f(-ARENA_LIMIT, ARENA_LIMIT + tile_size, barrier_height)
    
    glColor3f(0.0, 1.0, 1.0)
    glVertex3f(-ARENA_LIMIT, -ARENA_LIMIT, 0)
    glVertex3f(ARENA_LIMIT + tile_size, -ARENA_LIMIT, 0)
    glVertex3f(ARENA_LIMIT + tile_size, -ARENA_LIMIT, barrier_height)
    glVertex3f(-ARENA_LIMIT, -ARENA_LIMIT, barrier_height)
    
    glEnd()

def draw_player():
    global hero_pos, gun_angle, game_running
    
    glPushMatrix()
    
    glTranslatef(hero_pos[0], hero_pos[1], hero_pos[2])
    glRotatef(gun_angle, 0, 0, 1)
    
    if not game_running:
        glRotatef(-85, 1, 0, 0)
    
    glPushMatrix()
    glTranslatef(0, 0, 45)
    glColor3f(0.2, 0.8, 0.2)
    glutSolidCube(35)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, 0, 85)
    glColor3f(1.0, 0.8, 0.6)
    gluSphere(gluNewQuadric(), 18, 12, 12)
    glPopMatrix()
    
    limb_coords = [(-12, 0, 0), (12, 0, 0)]
    
    for idx, (px, py, pz) in enumerate(limb_coords):
        glPushMatrix()
        glTranslatef(px, py, pz)
        glColor3f(0.0, 0.0, 1.0)
        gluCylinder(gluNewQuadric(), 6, 9, 45, 10, 10)
        glPopMatrix()
    
    glPushMatrix()
    glTranslatef(-22, 0, 55)
    glRotatef(85, 0, 1, 0)
    glColor3f(1.0, 0.8, 0.6)
    gluCylinder(gluNewQuadric(), 5, 5, 28, 10, 10)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(22, 0, 55)
    glRotatef(85, 0, 1, 0)
    glColor3f(0.4, 0.4, 0.4)
    gluCylinder(gluNewQuadric(), 4, 4, 45, 10, 10)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(45, 0, 55)
    glRotatef(85, 0, 1, 0)
    glColor3f(0.2, 0.2, 0.2)
    gluCylinder(gluNewQuadric(), 3, 3, 25, 8, 8)
    glPopMatrix()
    
    glPopMatrix()

def draw_enemy(x_loc, y_loc, z_loc):
    
    global enemy_scale
    
    glPushMatrix()
    glTranslatef(x_loc, y_loc, z_loc)
    glScalef(enemy_scale, enemy_scale, enemy_scale)
    
    glPushMatrix()
    glTranslatef(0, 0, target_size)
    glColor3f(1.0, 0.0, 0.0)
    gluSphere(gluNewQuadric(), target_size, 15, 15)  
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, 0, target_size + 45)  
    glColor3f(0.0, 0.0, 0.0)  
    gluSphere(gluNewQuadric(), 20, 12, 12)  
    glPopMatrix()
    
    glPopMatrix()

def draw_bullet(bx, by, bz):
    
    glPushMatrix()
    glTranslatef(bx, by, bz)
    glColor3f(1.0, 1.0, 0.0)
    glutSolidCube(bullet_size)
    glPopMatrix()

def fire_bullet():
    
    global ammunition, hero_pos, gun_angle
    
    fire_angle = math.radians(gun_angle + 270)
    gun_offset = 75
    
    spawn_x = hero_pos[0] + gun_offset * math.cos(fire_angle)
    spawn_y = hero_pos[1] + gun_offset * math.sin(fire_angle)
    spawn_z = hero_pos[2] + 55
    
    ammunition.append([spawn_x, spawn_y, spawn_z, gun_angle])

def move_bullets():
    
    global ammunition, shots_missed, game_running
    
    expired_bullets = []
    
    for bullet in ammunition:
        travel_angle = math.radians(bullet[3] + 270)
        bullet[0] += bullet_speed * math.cos(travel_angle)
        bullet[1] += bullet_speed * math.sin(travel_angle)
        
        edge_buffer = 120
        if (abs(bullet[0]) > ARENA_LIMIT + edge_buffer or 
            abs(bullet[1]) > ARENA_LIMIT + edge_buffer):
            expired_bullets.append(bullet)
            shots_missed += 1
    
    for bullet in expired_bullets:
        if bullet in ammunition:
            ammunition.remove(bullet)
    
    if shots_missed >= MAX_MISSES:
        game_running = False

def spawn_enemies():
    
    global targets
    
    targets.clear()
    attempts = 0
    max_spawn_tries = 100
    
    while len(targets) < ENEMY_COUNT and attempts < max_spawn_tries:
        rand_x = random.randint(-ARENA_LIMIT + 120, ARENA_LIMIT - 120)
        rand_y = random.randint(-ARENA_LIMIT + 120, ARENA_LIMIT - 120)
        
        player_distance = ((rand_x - hero_pos[0])**2 + 
                          (rand_y - hero_pos[1])**2)**0.5
        
        if player_distance > 180:
            targets.append([rand_x, rand_y, 0])
        
        attempts += 1

def move_enemies():
    
    global targets, lives_left, game_running, score
    
    hit_list = []
    
    for enemy in targets:
        delta_x = hero_pos[0] - enemy[0]
        delta_y = hero_pos[1] - enemy[1]
        distance = math.hypot(delta_x, delta_y)
        
        if distance > 0:
            step_x = target_speed * (delta_x / distance)
            step_y = target_speed * (delta_y / distance)
            enemy[0] += step_x
            enemy[1] += step_y
        
        if distance < 55:
            lives_left -= 1
            hit_list.append(enemy)
            
            if lives_left <= 0:
                game_running = False
    
    for enemy in hit_list:
        if enemy in targets:
            targets.remove(enemy)
            
            retry = 0
            while retry < 20:
                respawn_x = random.randint(-ARENA_LIMIT + 120, ARENA_LIMIT - 120)
                respawn_y = random.randint(-ARENA_LIMIT + 120, ARENA_LIMIT - 120)
                
                if math.hypot(respawn_x - hero_pos[0], respawn_y - hero_pos[1]) > 180:
                    targets.append([respawn_x, respawn_y, 0])
                    break
                retry += 1

def detect_hits():
    
    global ammunition, targets, score
    
    bullets_to_remove = []
    enemies_to_remove = []
    
    for bullet in ammunition:
        for enemy in targets:
            diff_x = bullet[0] - enemy[0]
            diff_y = bullet[1] - enemy[1]
            diff_z = bullet[2] - (enemy[2] + target_size)
            
            hit_distance = math.sqrt(diff_x**2 + diff_y**2 + diff_z**2)
            
            if hit_distance < target_size:
                bullets_to_remove.append(bullet)
                enemies_to_remove.append(enemy)
                score += 1
                break
    
    for bullet in bullets_to_remove:
        if bullet in ammunition:
            ammunition.remove(bullet)
    
    for enemy in enemies_to_remove:
        if enemy in targets:
            targets.remove(enemy)
            
            for tries in range(25):
                new_spawn_x = random.uniform(-ARENA_LIMIT + 120, ARENA_LIMIT - 120)
                new_spawn_y = random.uniform(-ARENA_LIMIT + 120, ARENA_LIMIT - 120)
                
                if math.hypot(new_spawn_x - hero_pos[0], new_spawn_y - hero_pos[1]) > 180:
                    targets.append([new_spawn_x, new_spawn_y, 0])
                    break

def auto_fire_mode():
    
    global gun_angle, auto_aim_on
    
    if not auto_aim_on:
        return
    
    gun_angle = (gun_angle + 3) % 360
    
    for enemy in targets:
        aim_x = enemy[0] - hero_pos[0]
        aim_y = enemy[1] - hero_pos[1]
        
        aim_angle = math.degrees(math.atan2(aim_y, aim_x)) - 90
        aim_angle = (aim_angle + 360) % 360
        
        angle_diff = abs(gun_angle - aim_angle)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        
        if angle_diff < 8:
            fire_bullet()
            break

def pulse_enemy_size():
    
    global enemy_scale, scale_direction
    
    enemy_scale += scale_direction * 0.015
    if enemy_scale > 1.4:
        scale_direction = -1
    elif enemy_scale < 0.6:
        scale_direction = 1

def keyboardListener(key, x, y):
    
    global hero_pos, gun_angle, auto_aim_on, cheat_vision_active, game_running
    global lives_left, score, shots_missed, first_person_view
    
    if game_running:
        if key == b'w':
            move_rad = math.radians(gun_angle + 270)
            next_x = hero_pos[0] + player_speed * math.cos(move_rad)
            next_y = hero_pos[1] + player_speed * math.sin(move_rad)
            
            if -ARENA_LIMIT < next_x < ARENA_LIMIT:
                hero_pos[0] = next_x
            if -ARENA_LIMIT < next_y < ARENA_LIMIT:
                hero_pos[1] = next_y

        if key == b's':
            move_rad = math.radians(gun_angle + 270)
            next_x = hero_pos[0] - player_speed * math.cos(move_rad)
            next_y = hero_pos[1] - player_speed * math.sin(move_rad)
            
            if -ARENA_LIMIT < next_x < ARENA_LIMIT:
                hero_pos[0] = next_x
            if -ARENA_LIMIT < next_y < ARENA_LIMIT:
                hero_pos[1] = next_y

        if key == b'a':
            gun_angle += rotation_speed
        if key == b'd':
            gun_angle -= rotation_speed

        if key == b'c':
            auto_aim_on = not auto_aim_on

        if key == b'v':
            if first_person_view and auto_aim_on:
                cheat_vision_active = not cheat_vision_active

    if key == b'r':
        game_running = True
        first_person_view = False
        auto_aim_on = False
        cheat_vision_active = False
        hero_pos = [0, 0, 0]
        gun_angle = 0
        lives_left = 5
        score = 0
        shots_missed = 0
        ammunition.clear()
        spawn_enemies()

def specialKeyListener(key, x, y):
    
    global observer_pos, observer_angle, observer_height
    
    temp_x, temp_y, temp_z = observer_pos
    
    if key == GLUT_KEY_UP:
        observer_height -= 25
        temp_z = observer_height

    if key == GLUT_KEY_DOWN:
        observer_height += 25
        temp_z = observer_height

    if key == GLUT_KEY_LEFT:
        observer_angle -= 6

    if key == GLUT_KEY_RIGHT:
        observer_angle += 6

    temp_x = 750 * math.sin(math.radians(observer_angle))
    temp_y = 750 * math.cos(math.radians(observer_angle))
    
    observer_pos = [temp_x, temp_y, temp_z]

def mouseListener(button, state, x, y):
    
    global first_person_view, game_running
    
    if game_running:
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            fire_bullet()

        if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
            first_person_view = not first_person_view

def setupCamera():
    
    global observer_pos, first_person_view, hero_pos, gun_angle, cheat_vision_active, auto_aim_on
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if first_person_view:
        look_rad = math.radians(gun_angle + 270)
        cam_x = hero_pos[0] + 25 * math.cos(look_rad)
        cam_y = hero_pos[1] + 25 * math.sin(look_rad)
        cam_z = hero_pos[2] + 75
        
        if auto_aim_on and not cheat_vision_active:
            cam_x = hero_pos[0]
            cam_y = hero_pos[1] - 50
            cam_z = hero_pos[2] + 180
            
            gluLookAt(cam_x, cam_y, cam_z,
                      hero_pos[0] + 80, hero_pos[1], hero_pos[2],
                      0, 0, 1)
        else:
            focus_x = cam_x + 90 * math.cos(look_rad)
            focus_y = cam_y + 90 * math.sin(look_rad)
            focus_z = cam_z
            
            gluLookAt(cam_x, cam_y, cam_z,
                      focus_x, focus_y, focus_z,
                      0, 0, 1)
    else:
        obs_x, obs_y, obs_z = observer_pos
        gluLookAt(obs_x, obs_y, obs_z,
                  0, 0, 0,
                  0, 0, 1)

def idle():
    
    if game_running:
        move_bullets()
        move_enemies()
        detect_hits()
        pulse_enemy_size()
        auto_fire_mode()
    
    glutPostRedisplay()

def showScreen():
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

    setupCamera()
    
    draw_arena_floor()
    draw_player()
    
    for enemy in targets:
        draw_enemy(enemy[0], enemy[1], enemy[2])
    
    for bullet in ammunition:
        draw_bullet(bullet[0], bullet[1], bullet[2])

    if game_running:
        draw_text(10, 770, f"Player Life Remaining: {lives_left}")
        draw_text(10, 740, f"Game Score: {score}")
        draw_text(10, 710, f"Player Bullet Missed: {shots_missed}")
        draw_text(10, 680, f"View: {'First Person' if first_person_view else 'Third Person'}")
        if auto_aim_on:
            draw_text(10, 650, "CHEAT ACTIVE")
    else:
        draw_text(10, 770, "GAME FINISHED!")
        draw_text(10, 740, f"Final Score: {score}")
        draw_text(10, 710, "Press R to restart")

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(SCREEN_WIDTH, SCREEN_HEIGHT)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Bullet Frenzy - 3D Game")

    spawn_enemies()

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()