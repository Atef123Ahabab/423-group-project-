from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
USE_3D_MODE = False
camera_pos = (0, 500, 500)
camera_field_of_view = 120
GRID_LENGTH = 600
player_x_2d = 550.0
player_y_2d = 150.0
player_base_y = 150.0
ground_y = 150.0
player_lane = 1
lanes_2d = [450, 550, 650, 750]
window_width = 1200
window_height = 800
player_x = -50
player_y = -400
player_z = 30
lanes_3d = [-150, -50, 50, 150]
player_velocity_x = 0
player_velocity_y = 0
player_is_jumping = False
player_is_sliding = False
player_speed = 2.0
base_speed = 2.0
max_speed = 15.0
acceleration = 0.02
speed_increment = 0.02
deceleration = 0.5
speed_increase_timer = 0
slide_duration = 0
slide_duration_frames = 30
current_lane = 1
jump_velocity = 0
gravity_3d = -1.5
gravity_2d = -1.2
jump_strength_3d = 20
jump_strength_2d = 18
ground_level = 30
animation_frame = 0
leg_swing = 0
arm_swing = 0
body_tilt = 0
leg_angle = 0
arm_angle = 0
player_width = 30
player_height = 40
def draw_filled_rect(x, y, w, h):
    glBegin(GL_TRIANGLES)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x, y + h)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()
def draw_circle_2d(cx, cy, radius, filled=True):
    num_segments = 20
    if filled:
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(cx, cy)
        for i in range(num_segments + 1):
            angle = 2.0 * math.pi * i / num_segments
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            glVertex2f(x, y)
        glEnd()
    else:
        glBegin(GL_LINE_LOOP)
        for i in range(num_segments):
            angle = 2.0 * math.pi * i / num_segments
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            glVertex2f(x, y)
        glEnd()
def draw_skateboard_character_3d():
    global animation_frame, leg_swing, arm_swing, body_tilt, player_z
    global player_is_jumping, player_is_sliding, player_speed
    glPushMatrix()
    glTranslatef(player_x, player_y, player_z)
    if not player_is_jumping and not player_is_sliding:
        animation_frame += player_speed * 0.5
        leg_swing = math.sin(animation_frame * 0.1) * 15
        arm_swing = math.cos(animation_frame * 0.1) * 10
        body_tilt = math.sin(animation_frame * 0.05) * 3
    else:
        body_tilt = 0
    glRotatef(body_tilt, 1, 0, 0)
    glPushMatrix()
    glTranslatef(0, 0, -25)
    glColor3f(0.9, 0.5, 0.1)
    glScalef(1.5, 0.3, 0.1)
    glutSolidCube(20)
    glColor3f(0.2, 0.2, 0.2)
    glTranslatef(-0.5, 0, -1)
    glScalef(0.3, 0.3, 1)
    glutSolidSphere(5, 8, 8)
    glTranslatef(1, 0, 0)
    glutSolidSphere(5, 8, 8)
    glPopMatrix()
    glPushMatrix()
    if player_is_sliding:
        glRotatef(45, 1, 0, 0)
    glColor3f(0.2, 0.4, 0.8)
    glScalef(1, 0.5, 1.5)
    glutSolidCube(25)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 0, 25)
    glColor3f(0.95, 0.8, 0.7)
    glutSolidSphere(10, 12, 12)
    glColor3f(0.9, 0.1, 0.1)
    glTranslatef(0, 0, 3)
    glScalef(1.1, 1.1, 0.8)
    glutSolidSphere(10, 12, 12)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-15, 0, 8)
    glRotatef(arm_swing, 1, 0, 0)
    glColor3f(0.95, 0.8, 0.7)
    glScalef(0.4, 0.4, 1.2)
    glutSolidCube(15)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(15, 0, 8)
    glRotatef(-arm_swing, 1, 0, 0)
    glColor3f(0.95, 0.8, 0.7)
    glScalef(0.4, 0.4, 1.2)
    glutSolidCube(15)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-8, 0, -15)
    if not player_is_jumping and not player_is_sliding:
        glRotatef(leg_swing, 1, 0, 0)
    glColor3f(0.1, 0.1, 0.5)
    glScalef(0.5, 0.5, 1.5)
    glutSolidCube(15)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(8, 0, -15)
    if not player_is_jumping and not player_is_sliding:
        glRotatef(-leg_swing, 1, 0, 0)
    glColor3f(0.1, 0.1, 0.5)
    glScalef(0.5, 0.5, 1.5)
    glutSolidCube(15)
    glPopMatrix()
    glPopMatrix()
def draw_skateboard_character_2d():
    global player_x_2d, player_y_2d, animation_frame
    global leg_angle, arm_angle, player_is_sliding, player_speed
    px = player_x_2d
    py = player_y_2d
    if player_is_sliding:
        py -= 15
        glColor3f(0.9, 0.5, 0.2)
        draw_filled_rect(px - 15, py - 5, 30, 8)
        glColor3f(0.2, 0.2, 0.2)
        draw_circle_2d(px - 10, py - 5, 4)
        draw_circle_2d(px + 10, py - 5, 4)
        glColor3f(0.2, 0.6, 0.9)
        draw_filled_rect(px - 10, py + 3, 20, 15)
        glColor3f(1.0, 0.8, 0.6)
        draw_circle_2d(px, py + 25, 8)
        glColor3f(1.0, 0.8, 0.6)
        draw_filled_rect(px - 5, py + 10, 15, 5)
        return
    glColor3f(0.9, 0.5, 0.2)
    draw_filled_rect(px - 15, py - 5, 30, 8)
    glColor3f(0.2, 0.2, 0.2)
    draw_circle_2d(px - 10, py - 5, 4)
    draw_circle_2d(px + 10, py - 5, 4)
    glColor3f(0.3, 0.3, 0.8)
    leg_offset = math.sin(animation_frame * 0.2) * 3
    draw_filled_rect(px - 10, py + 3, 6, 15 + leg_offset)
    draw_filled_rect(px + 4, py + 3, 6, 15 - leg_offset)
    glColor3f(0.2, 0.6, 0.9)
    draw_filled_rect(px - 10, py + 18, 20, 18)
    glColor3f(1.0, 0.8, 0.6)
    draw_circle_2d(px, py + 45, 8)
    glColor3f(0.9, 0.1, 0.1)
    draw_circle_2d(px, py + 48, 9, filled=False)
    draw_filled_rect(px - 9, py + 45, 18, 5)
    glColor3f(1.0, 0.8, 0.6)
    arm_offset = math.sin(animation_frame * 0.2) * 2
    draw_filled_rect(px - 15, py + 25 + arm_offset, 5, 12)
    draw_filled_rect(px + 10, py + 25 - arm_offset, 5, 12)
def draw_skateboard_character():
    if USE_3D_MODE:
        draw_skateboard_character_3d()
    else:
        draw_skateboard_character_2d()
def update_player_movement():
    if USE_3D_MODE:
        global player_x, player_z, player_velocity_x, player_speed
        global is_jumping, jump_velocity, is_sliding
        if player_speed < max_speed:
            player_speed += acceleration
        player_x += player_velocity_x
        player_velocity_x *= 0.85
        if player_x < -200:
            player_x = -200
        if player_x > 200:
            player_x = 200
        if is_jumping:
            player_z += jump_velocity
            jump_velocity += gravity
            if player_z <= ground_level:
                player_z = ground_level
                is_jumping = False
                jump_velocity = 0
                is_sliding = False
    else:
        global player_x_2d, player_y_2d, player_velocity_y, player_is_jumping
        global player_is_sliding, slide_duration, animation_frame
        if player_speed < max_speed:
            player_speed += speed_increment
        animation_frame += player_speed * 0.1
        if player_is_jumping:
            player_velocity_y += gravity_2d
            player_y_2d += player_velocity_y
            if player_y_2d <= ground_y:
                player_y_2d = ground_y
                player_velocity_y = 0
                player_is_jumping = False
        else:
            player_y_2d = ground_y
            player_velocity_y = 0
        if player_is_sliding:
            slide_duration -= 1
            if slide_duration <= 0:
                player_is_sliding = False
                slide_duration = 0
def handle_collision():
    global player_speed
    player_speed = max(base_speed, player_speed - deceleration)
def keyboardListener(key, x, y):
    if USE_3D_MODE:
        global player_velocity_x, is_jumping, jump_velocity, is_sliding
        if key == b'a':
            player_velocity_x = -8
        if key == b'd':
            player_velocity_x = 8
        if key == b'w' and not is_jumping:
            is_jumping = True
            jump_velocity = jump_strength
        if key == b's' and not is_jumping:
            is_sliding = True
        if key == b' ':
            handle_collision()
    else:
        global current_lane, player_is_jumping, player_velocity_y, player_is_sliding
        if key == b'a' or key == b'A':
            move_left()
        if key == b'd' or key == b'D':
            move_right()
        if key == b'w' or key == b'W':
            jump()
        if key == b's' or key == b'S':
            slide()
    glutPostRedisplay()
def move_left():
    global current_lane, player_x_2d
    if current_lane > 0:
        current_lane -= 1
        player_x_2d = lanes_2d[current_lane]
def move_right():
    global current_lane, player_x_2d
    if current_lane < len(lanes_2d) - 1:
        current_lane += 1
        player_x_2d = lanes_2d[current_lane]
def jump():
    global player_is_jumping, player_velocity_y
    if not player_is_jumping:
        player_is_jumping = True
        player_velocity_y = jump_strength_2d
def slide():
    global player_is_sliding, slide_duration
    if not player_is_jumping and not player_is_sliding:
        player_is_sliding = True
        slide_duration = slide_duration_frames
def get_player_position():
    if USE_3D_MODE:
        return (player_x, player_z)
    else:
        return (player_x_2d, player_y_2d)
def get_player_lane():
    return current_lane
def get_player_speed():
    return player_speed
def set_player_speed(new_speed):
    global player_speed
    player_speed = max(base_speed, min(new_speed, max_speed))
def is_player_jumping():
    if USE_3D_MODE:
        return is_jumping
    else:
        return player_is_jumping
def is_player_sliding():
    if USE_3D_MODE:
        return is_sliding
    else:
        return player_is_sliding
def reset_player():
    global player_x, player_z, player_x_2d, player_y_2d
    global current_lane, player_speed, player_velocity_y
    global is_jumping, player_is_jumping, is_sliding, player_is_sliding
    global animation_frame
    if USE_3D_MODE:
        player_x = 0
        player_z = 0
        is_jumping = False
        is_sliding = False
    else:
        current_lane = 1
        player_x_2d = lanes_2d[current_lane]
        player_y_2d = ground_y
        player_velocity_y = 0
        player_is_jumping = False
        player_is_sliding = False
    player_speed = base_speed
    animation_frame = 0
def get_character_width():
    return 30 if not player_is_sliding else 35
def get_character_height():
    return 55 if not player_is_sliding else 25
def specialKeyListener(key, x, y):
    if USE_3D_MODE:
        global camera_pos
        x, y, z = camera_pos
        if key == GLUT_KEY_LEFT:
            x -= 10
        if key == GLUT_KEY_RIGHT:
            x += 10
        if key == GLUT_KEY_UP:
            y -= 10
        if key == GLUT_KEY_DOWN:
            y += 10
        camera_pos = (x, y, z)
        glutPostRedisplay()
def mouseListener(button, state, x, y):
    pass
def draw_text(x, y, text, font=None):
    if font is None:
        try:
            font = GLUT_BITMAP_9_BY_15
        except:
            font = GLUT_BITMAP_HELVETICA_18
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        try:
            glutBitmapCharacter(font, ord(ch))
        except:
            pass
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(camera_field_of_view, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    x, y, z = camera_pos
    gluLookAt(x, y, z,
              0, 0, 0,
              0, 0, 1)
def idle():
    update_player_movement()
    glutPostRedisplay()
def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    if USE_3D_MODE:
        setupCamera()
        glBegin(GL_QUADS)
        glColor3f(0.3, 0.3, 0.3)
        glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
        glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
        glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
        glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
        glEnd()
        glColor3f(1, 1, 0)
        glBegin(GL_LINES)
        glVertex3f(-100, GRID_LENGTH, 1)
        glVertex3f(-100, -GRID_LENGTH, 1)
        glVertex3f(100, GRID_LENGTH, 1)
        glVertex3f(100, -GRID_LENGTH, 1)
        glEnd()
        draw_skateboard_character()
        draw_text(10, 770, f"Speed: {player_speed:.1f} | Max Speed: {max_speed}")
        draw_text(10, 740, f"Position: {player_x:.0f} | Height: {player_z:.0f}")
        draw_text(10, 710, f"Controls: A/D - Move | W - Jump | S - Slide | Space - Test Collision")
        if is_jumping:
            draw_text(10, 680, "JUMPING!")
        if is_sliding:
            draw_text(10, 680, "SLIDING!")
    else:
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, window_width, 0, window_height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glColor3f(0.2, 0.2, 0.3)
        draw_filled_rect(0, 0, window_width, window_height)
        glColor3f(0.3, 0.3, 0.3)
        draw_filled_rect(0, 0, window_width, ground_y + 10)
        glColor3f(1, 1, 0)
        for lane_x in lanes_2d:
            draw_filled_rect(lane_x - 2, 0, 4, window_height)
        draw_skateboard_character()
        draw_text(10, window_height - 30, 
                 f"Speed: {player_speed:.1f} | Lane: {current_lane + 1}/3")
    glutSwapBuffers()
def init():
    glClearColor(0.53, 0.81, 0.92, 1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Naimur's Features: Character, Movement & Speed System")
    init()
    glutDisplayFunc(showScreen)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutMainLoop()
if __name__ == "__main__":
    print("=" * 70)
    print("NAIMUR'S FEATURE MODULE")
    print("=" * 70)
    print("Running in", "3D MODE" if USE_3D_MODE else "2D MODE")
    print("\nFEATURES IMPLEMENTED:")
    print("1. Skateboard Character Design & Animation")
    print("2. Movement Controls (A/D left/right, W jump, S slide)")
    print("3. Speed System (gradual acceleration)")
    print("\nCONTROLS:")
    print("  A/D     - Move left/right")
    print("  W       - Jump")
    print("  S       - Slide")
    if USE_3D_MODE:
        print("  Arrows  - Camera control (3D mode)")
        print("  Space   - Test collision")
    print("\nStarting game...")
    print("=" * 70)
    main()
else:
    print(f"[Naimur Module] Loaded in {'3D' if USE_3D_MODE else '2D'} mode")