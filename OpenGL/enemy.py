from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# Display and world configuration
WINDOW_W, WINDOW_H = 1000, 800
WORLD_BOUNDARY = 600
perspective_fov = 120

# Camera system variables
cam_position = [0, 450, 450]
cam_rotation = 0
cam_elevation = 450
view_mode_fps = False

# Game state management
is_game_active = True
cheat_enabled = False
auto_target_mode = False

# Player character properties
character_location = [0, 0, 0]
weapon_direction = 0
move_speed = 12
turn_rate = 6
health_points = 5
points_earned = 0

# Projectile system
projectile_list = []
missed_shots = 0
shot_limit = 10
projectile_velocity = 18
projectile_dimension = 8

# Adversary system
adversary_list = []
total_adversaries = 5
adversary_velocity = 0.3
adversary_radius = 40
size_multiplier = 1.0
scaling_factor = 1

def render_text(pos_x, pos_y, message, typeface=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    gluOrtho2D(0, WINDOW_W, 0, WINDOW_H)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(pos_x, pos_y)
    for character in message:
        glutBitmapCharacter(typeface, ord(character))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def create_floor_pattern():
    tile_dimension = 100
    glBegin(GL_QUADS)
    
    #purple/white checkered pattern 
    for grid_x in range(-WORLD_BOUNDARY, WORLD_BOUNDARY + tile_dimension, tile_dimension):
        for grid_y in range(-WORLD_BOUNDARY, WORLD_BOUNDARY + tile_dimension, tile_dimension):
            # Checkered pattern calculation 
            color_check = ((grid_x + grid_y) // tile_dimension) % 2
            if color_check == 0:
                glColor3f(1.0, 1.0, 1.0)  # Pure white squares
            else:
                glColor3f(0.7, 0.5, 0.95)  # Purple squares 
            
            glVertex3f(grid_x, grid_y, 0)
            glVertex3f(grid_x + tile_dimension, grid_y, 0)
            glVertex3f(grid_x + tile_dimension, grid_y + tile_dimension, 0)
            glVertex3f(grid_x, grid_y + tile_dimension, 0)
    
    glEnd()
    
    # Create boundary walls 
    wall_height = 100
    glBegin(GL_QUADS)
    
    # Left Wall - Green 
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(-WORLD_BOUNDARY, -WORLD_BOUNDARY, 0)
    glVertex3f(-WORLD_BOUNDARY, WORLD_BOUNDARY + tile_dimension, 0)
    glVertex3f(-WORLD_BOUNDARY, WORLD_BOUNDARY + tile_dimension, wall_height)
    glVertex3f(-WORLD_BOUNDARY, -WORLD_BOUNDARY, wall_height)
    
    # Right Wall - Blue 
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(WORLD_BOUNDARY + tile_dimension, -WORLD_BOUNDARY, 0)
    glVertex3f(WORLD_BOUNDARY + tile_dimension, WORLD_BOUNDARY + tile_dimension, 0)
    glVertex3f(WORLD_BOUNDARY + tile_dimension, WORLD_BOUNDARY + tile_dimension, wall_height)
    glVertex3f(WORLD_BOUNDARY + tile_dimension, -WORLD_BOUNDARY, wall_height)
    
    # Bottom Wall - White 
    glColor3f(1.0, 1.0, 1.0)
    glVertex3f(-WORLD_BOUNDARY, WORLD_BOUNDARY + tile_dimension, 0)
    glVertex3f(WORLD_BOUNDARY + tile_dimension, WORLD_BOUNDARY + tile_dimension, 0)
    glVertex3f(WORLD_BOUNDARY + tile_dimension, WORLD_BOUNDARY + tile_dimension, wall_height)
    glVertex3f(-WORLD_BOUNDARY, WORLD_BOUNDARY + tile_dimension, wall_height)
    
    # Top Wall - Cyan 
    glColor3f(0.0, 1.0, 1.0)
    glVertex3f(-WORLD_BOUNDARY, -WORLD_BOUNDARY, 0)
    glVertex3f(WORLD_BOUNDARY + tile_dimension, -WORLD_BOUNDARY, 0)
    glVertex3f(WORLD_BOUNDARY + tile_dimension, -WORLD_BOUNDARY, wall_height)
    glVertex3f(-WORLD_BOUNDARY, -WORLD_BOUNDARY, wall_height)
    
    glEnd()

def render_character():
    global character_location, weapon_direction, is_game_active
    
    glPushMatrix()
    
    glTranslatef(character_location[0], character_location[1], character_location[2])
    glRotatef(weapon_direction, 0, 0, 1)
    
    # Death animation when game over
    if not is_game_active:
        glRotatef(-85, 1, 0, 0)
    
    # Body (Cuboid) 
    glPushMatrix()
    glTranslatef(0, 0, 45)
    glColor3f(0.2, 0.8, 0.2)  # Bright green body
    glutSolidCube(35)
    glPopMatrix()
    
    # Head (Sphere) 
    glPushMatrix()
    glTranslatef(0, 0, 85)
    glColor3f(1.0, 0.8, 0.6)  # Skin color
    gluSphere(gluNewQuadric(), 18, 12, 12)
    glPopMatrix()
    
    # Legs (Cylinders) - blue pants 
    leg_positions = [(-12, 0, 0), (12, 0, 0)]
    
    for i, (x, y, z) in enumerate(leg_positions):
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(0.0, 0.0, 1.0)  # Blue legs
        gluCylinder(gluNewQuadric(), 6, 9, 45, 10, 10)
        glPopMatrix()
    
    # Left arm (Cylinder)
    glPushMatrix()
    glTranslatef(-22, 0, 55)
    glRotatef(85, 0, 1, 0)
    glColor3f(1.0, 0.8, 0.6)  # Skin tone
    gluCylinder(gluNewQuadric(), 5, 5, 28, 10, 10)
    glPopMatrix()
    
    # Gun (Cylinders) - gray weapon
    glPushMatrix()
    glTranslatef(22, 0, 55)
    glRotatef(85, 0, 1, 0)
    glColor3f(0.4, 0.4, 0.4)  # Dark gray gun
    gluCylinder(gluNewQuadric(), 4, 4, 45, 10, 10)
    glPopMatrix()
    
    # Gun barrel
    glPushMatrix()
    glTranslatef(45, 0, 55)
    glRotatef(85, 0, 1, 0)
    glColor3f(0.2, 0.2, 0.2)  # Darker gun tip
    gluCylinder(gluNewQuadric(), 3, 3, 25, 8, 8)
    glPopMatrix()
    
    glPopMatrix()

def render_adversary(pos_x, pos_y, pos_z):
    
    global size_multiplier
    
    glPushMatrix()
    glTranslatef(pos_x, pos_y, pos_z)
    glScalef(size_multiplier, size_multiplier, size_multiplier)
    
    # Main body sphere - positioned at ground level + radius
    glPushMatrix()
    glTranslatef(0, 0, adversary_radius)  # Lift sphere so it sits on ground
    glColor3f(1.0, 0.0, 0.0)  # Pure bright red 
    gluSphere(gluNewQuadric(), adversary_radius, 15, 15)  
    glPopMatrix()
    
    # Head sphere 
    glPushMatrix()
    glTranslatef(0, 0, adversary_radius + 45)  
    glColor3f(0.0, 0.0, 0.0)  
    gluSphere(gluNewQuadric(), 20, 12, 12)  
    glPopMatrix()
    
    glPopMatrix()

def render_projectile(pos_x, pos_y, pos_z):
    
    glPushMatrix()
    glTranslatef(pos_x, pos_y, pos_z)
    glColor3f(1.0, 1.0, 0.0)  # Bright yellow bullets
    glutSolidCube(projectile_dimension)
    glPopMatrix()

def launch_projectile():
    
    global projectile_list, character_location, weapon_direction
    
    angle_radians = math.radians(weapon_direction + 270)
    weapon_offset = 75
    
    start_x = character_location[0] + weapon_offset * math.cos(angle_radians)
    start_y = character_location[1] + weapon_offset * math.sin(angle_radians)
    start_z = character_location[2] + 55
    
    projectile_list.append([start_x, start_y, start_z, weapon_direction])

def update_projectiles():
    
    global projectile_list, missed_shots, is_game_active
    
    remove_list = []
    
    for projectile in projectile_list:
        movement_angle = math.radians(projectile[3] + 270)
        projectile[0] += projectile_velocity * math.cos(movement_angle)
        projectile[1] += projectile_velocity * math.sin(movement_angle)
        
        boundary_buffer = 120
        if (abs(projectile[0]) > WORLD_BOUNDARY + boundary_buffer or 
            abs(projectile[1]) > WORLD_BOUNDARY + boundary_buffer):
            remove_list.append(projectile)
            missed_shots += 1
    
    for projectile in remove_list:
        if projectile in projectile_list:
            projectile_list.remove(projectile)
    
    if missed_shots >= shot_limit:
        is_game_active = False

def initialize_adversaries():
    
    global adversary_list
    
    adversary_list.clear()
    spawn_attempts = 0
    max_attempts = 100
    
    while len(adversary_list) < total_adversaries and spawn_attempts < max_attempts:
        spawn_x = random.randint(-WORLD_BOUNDARY + 120, WORLD_BOUNDARY - 120)
        spawn_y = random.randint(-WORLD_BOUNDARY + 120, WORLD_BOUNDARY - 120)
        
        distance_to_player = ((spawn_x - character_location[0])**2 + 
                             (spawn_y - character_location[1])**2)**0.5
        
        if distance_to_player > 180:
            adversary_list.append([spawn_x, spawn_y, 0])
        
        spawn_attempts += 1

def update_adversaries():
    
    global adversary_list, health_points, is_game_active, points_earned
    
    collision_list = []
    
    for adversary in adversary_list:
        direction_x = character_location[0] - adversary[0]
        direction_y = character_location[1] - adversary[1]
        total_distance = math.hypot(direction_x, direction_y)
        
        if total_distance > 0:
            move_x = adversary_velocity * (direction_x / total_distance)
            move_y = adversary_velocity * (direction_y / total_distance)
            adversary[0] += move_x
            adversary[1] += move_y
        
        if total_distance < 55:
            health_points -= 1
            collision_list.append(adversary)
            
            if health_points <= 0:
                is_game_active = False
    
    for adversary in collision_list:
        if adversary in adversary_list:
            adversary_list.remove(adversary)
            
            respawn_attempts = 0
            while respawn_attempts < 20:
                new_x = random.randint(-WORLD_BOUNDARY + 120, WORLD_BOUNDARY - 120)
                new_y = random.randint(-WORLD_BOUNDARY + 120, WORLD_BOUNDARY - 120)
                
                if math.hypot(new_x - character_location[0], new_y - character_location[1]) > 180:
                    adversary_list.append([new_x, new_y, 0])
                    break
                respawn_attempts += 1

def check_combat_collisions():
    
    global projectile_list, adversary_list, points_earned
    
    hit_projectiles = []
    hit_adversaries = []
    
    for projectile in projectile_list:
        for adversary in adversary_list:
            distance_x = projectile[0] - adversary[0]
            distance_y = projectile[1] - adversary[1]
            distance_z = projectile[2] - (adversary[2] + adversary_radius)
            
            collision_distance = math.sqrt(distance_x**2 + distance_y**2 + distance_z**2)
            
            if collision_distance < adversary_radius:
                hit_projectiles.append(projectile)
                hit_adversaries.append(adversary)
                points_earned += 1
                break
    
    for projectile in hit_projectiles:
        if projectile in projectile_list:
            projectile_list.remove(projectile)
    
    for adversary in hit_adversaries:
        if adversary in adversary_list:
            adversary_list.remove(adversary)
            
            for attempt in range(25):
                spawn_x = random.uniform(-WORLD_BOUNDARY + 120, WORLD_BOUNDARY - 120)
                spawn_y = random.uniform(-WORLD_BOUNDARY + 120, WORLD_BOUNDARY - 120)
                
                if math.hypot(spawn_x - character_location[0], spawn_y - character_location[1]) > 180:
                    adversary_list.append([spawn_x, spawn_y, 0])
                    break

def cheat_auto_combat():
    
    global weapon_direction, cheat_enabled
    
    if not cheat_enabled:
        return
    
    weapon_direction = (weapon_direction + 3) % 360
    
    for adversary in adversary_list:
        target_x = adversary[0] - character_location[0]
        target_y = adversary[1] - character_location[1]
        
        target_angle = math.degrees(math.atan2(target_y, target_x)) - 90
        target_angle = (target_angle + 360) % 360
        
        angle_difference = abs(weapon_direction - target_angle)
        if angle_difference > 180:
            angle_difference = 360 - angle_difference
        
        if angle_difference < 8:
            launch_projectile()
            break

def animate_adversary_scaling():
    
    global size_multiplier, scaling_factor
    
    size_multiplier += scaling_factor * 0.015
    if size_multiplier > 1.4:
        scaling_factor = -1
    elif size_multiplier < 0.6:
        scaling_factor = 1

def keyboardListener(key, x, y):
    
    global character_location, weapon_direction, cheat_enabled, auto_target_mode, is_game_active
    global health_points, points_earned, missed_shots, view_mode_fps
    
    if is_game_active:
        if key == b'w':
            angle_rad = math.radians(weapon_direction + 270)
            new_x = character_location[0] + move_speed * math.cos(angle_rad)
            new_y = character_location[1] + move_speed * math.sin(angle_rad)
            
            if -WORLD_BOUNDARY < new_x < WORLD_BOUNDARY:
                character_location[0] = new_x
            if -WORLD_BOUNDARY < new_y < WORLD_BOUNDARY:
                character_location[1] = new_y

        if key == b's':
            angle_rad = math.radians(weapon_direction + 270)
            new_x = character_location[0] - move_speed * math.cos(angle_rad)
            new_y = character_location[1] - move_speed * math.sin(angle_rad)
            
            if -WORLD_BOUNDARY < new_x < WORLD_BOUNDARY:
                character_location[0] = new_x
            if -WORLD_BOUNDARY < new_y < WORLD_BOUNDARY:
                character_location[1] = new_y

        if key == b'a':
            weapon_direction += turn_rate
        if key == b'd':
            weapon_direction -= turn_rate

        if key == b'c':
            cheat_enabled = not cheat_enabled

        if key == b'v':
            if view_mode_fps and cheat_enabled:
                auto_target_mode = not auto_target_mode

    if key == b'r':
        is_game_active = True
        view_mode_fps = False
        cheat_enabled = False
        auto_target_mode = False
        character_location = [0, 0, 0]
        weapon_direction = 0
        health_points = 5
        points_earned = 0
        missed_shots = 0
        projectile_list.clear()
        initialize_adversaries()

def specialKeyListener(key, x, y):
    
    global cam_position, cam_rotation, cam_elevation
    
    current_x, current_y, current_z = cam_position
    
    if key == GLUT_KEY_UP:
        cam_elevation -= 25
        current_z = cam_elevation

    if key == GLUT_KEY_DOWN:
        cam_elevation += 25
        current_z = cam_elevation

    if key == GLUT_KEY_LEFT:
        cam_rotation -= 6

    if key == GLUT_KEY_RIGHT:
        cam_rotation += 6

    current_x = 750 * math.sin(math.radians(cam_rotation))
    current_y = 750 * math.cos(math.radians(cam_rotation))
    
    cam_position = [current_x, current_y, current_z]

def mouseListener(button, state, x, y):
    
    global view_mode_fps, is_game_active
    
    if is_game_active:
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            launch_projectile()

        if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
            view_mode_fps = not view_mode_fps

def setupCamera():
    
    global cam_position, view_mode_fps, character_location, weapon_direction, auto_target_mode, cheat_enabled
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(perspective_fov, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if view_mode_fps:
        view_angle = math.radians(weapon_direction + 270)
        eye_x = character_location[0] + 25 * math.cos(view_angle)
        eye_y = character_location[1] + 25 * math.sin(view_angle)
        eye_z = character_location[2] + 75
        
        if cheat_enabled and not auto_target_mode:
            eye_x = character_location[0]
            eye_y = character_location[1] - 50
            eye_z = character_location[2] + 180
            
            gluLookAt(eye_x, eye_y, eye_z,
                      character_location[0] + 80, character_location[1], character_location[2],
                      0, 0, 1)
        else:
            target_x = eye_x + 90 * math.cos(view_angle)
            target_y = eye_y + 90 * math.sin(view_angle)
            target_z = eye_z
            
            gluLookAt(eye_x, eye_y, eye_z,
                      target_x, target_y, target_z,
                      0, 0, 1)
    else:
        cam_x, cam_y, cam_z = cam_position
        gluLookAt(cam_x, cam_y, cam_z,
                  0, 0, 0,
                  0, 0, 1)

def idle():
    
    if is_game_active:
        update_projectiles()
        update_adversaries()
        check_combat_collisions()
        animate_adversary_scaling()
        cheat_auto_combat()
    
    glutPostRedisplay()

def showScreen():
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_W, WINDOW_H)

    setupCamera()
    
    # Render game world
    create_floor_pattern()
    render_character()
    
    # Render game objects
    for adversary in adversary_list:
        render_adversary(adversary[0], adversary[1], adversary[2])
    
    for projectile in projectile_list:
        render_projectile(projectile[0], projectile[1], projectile[2])

    # Display UI 
    if is_game_active:
        render_text(10, 770, f"Player Life Remaining: {health_points}")
        render_text(10, 740, f"Game Score: {points_earned}")
        render_text(10, 710, f"Player Bullet Missed: {missed_shots}")
        render_text(10, 680, f"View: {'First Person' if view_mode_fps else 'Third Person'}")
        if cheat_enabled:
            render_text(10, 650, "CHEAT ACTIVE")
    else:
        render_text(10, 770, "GAME FINISHED!")
        render_text(10, 740, f"Final Score: {points_earned}")
        render_text(10, 710, "Press R to restart")

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_W, WINDOW_H)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Bullet Frenzy - 3D Game")

    initialize_adversaries()

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()