from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# Camera-related variables
camera_pos = (0, 500, 500)
camera_field_of_view = 120
GRID_LENGTH = 600

# Player state variables
player_x = 0  # Horizontal position (-200 to 200 range for 3 lanes)
player_y = -400  # Fixed forward position
player_z = 30  # Height above ground

# Movement and animation states
player_velocity_x = 0  # Horizontal velocity
player_speed = 0  # Forward speed (increases over time)
base_speed = 2  # Starting speed
max_speed = 15  # Maximum speed
acceleration = 0.02  # Speed increase rate
deceleration = 0.5  # Speed reduction on collision

# Jump mechanics
is_jumping = False
is_sliding = False
jump_velocity = 0
gravity = -1.5
jump_strength = 20
ground_level = 30

# Animation variables
animation_frame = 0
leg_swing = 0
arm_swing = 0
body_tilt = 0


def draw_skateboard_character():
    """
    Draws the skateboard character with body parts and animations.
    Handles running, jumping, and falling animations.
    """
    global animation_frame, leg_swing, arm_swing, body_tilt, player_z, is_jumping, is_sliding
    
    glPushMatrix()
    glTranslatef(player_x, player_y, player_z)
    
    # Calculate animation values based on speed
    if not is_jumping and not is_sliding:
        animation_frame += player_speed * 0.5
        leg_swing = math.sin(animation_frame * 0.1) * 15
        arm_swing = math.cos(animation_frame * 0.1) * 10
        body_tilt = math.sin(animation_frame * 0.05) * 3
    else:
        body_tilt = 0
    
    # Apply body tilt for running animation
    glRotatef(body_tilt, 1, 0, 0)
    
    # SKATEBOARD
    glPushMatrix()
    glTranslatef(0, 0, -25)
    glColor3f(0.9, 0.5, 0.1)  # Orange skateboard
    glScalef(1.5, 0.3, 0.1)
    glutSolidCube(20)
    
    # Skateboard wheels
    glColor3f(0.2, 0.2, 0.2)
    glTranslatef(-0.5, 0, -1)
    glScalef(0.3, 0.3, 1)
    glutSolidSphere(5, 8, 8)
    glTranslatef(1, 0, 0)
    glutSolidSphere(5, 8, 8)
    glPopMatrix()
    
    # BODY (torso)
    glPushMatrix()
    if is_sliding:
        glRotatef(45, 1, 0, 0)  # Lean back when sliding
    glColor3f(0.2, 0.4, 0.8)  # Blue shirt
    glScalef(1, 0.5, 1.5)
    glutSolidCube(25)
    glPopMatrix()
    
    # HEAD
    glPushMatrix()
    glTranslatef(0, 0, 25)
    glColor3f(0.95, 0.8, 0.7)  # Skin tone
    glutSolidSphere(10, 12, 12)
    
    # Helmet
    glColor3f(0.9, 0.1, 0.1)  # Red helmet
    glTranslatef(0, 0, 3)
    glScalef(1.1, 1.1, 0.8)
    glutSolidSphere(10, 12, 12)
    glPopMatrix()
    
    # LEFT ARM
    glPushMatrix()
    glTranslatef(-15, 0, 8)
    glRotatef(arm_swing, 1, 0, 0)  # Arm swing animation
    glColor3f(0.95, 0.8, 0.7)
    glScalef(0.4, 0.4, 1.2)
    glutSolidCube(15)
    glPopMatrix()
    
    # RIGHT ARM
    glPushMatrix()
    glTranslatef(15, 0, 8)
    glRotatef(-arm_swing, 1, 0, 0)  # Opposite arm swing
    glColor3f(0.95, 0.8, 0.7)
    glScalef(0.4, 0.4, 1.2)
    glutSolidCube(15)
    glPopMatrix()
    
    # LEFT LEG
    glPushMatrix()
    glTranslatef(-8, 0, -15)
    if not is_jumping and not is_sliding:
        glRotatef(leg_swing, 1, 0, 0)  # Leg swing for running
    glColor3f(0.1, 0.1, 0.5)  # Dark blue pants
    glScalef(0.5, 0.5, 1.5)
    glutSolidCube(15)
    glPopMatrix()
    
    # RIGHT LEG
    glPushMatrix()
    glTranslatef(8, 0, -15)
    if not is_jumping and not is_sliding:
        glRotatef(-leg_swing, 1, 0, 0)  # Opposite leg swing
    glColor3f(0.1, 0.1, 0.5)
    glScalef(0.5, 0.5, 1.5)
    glutSolidCube(15)
    glPopMatrix()
    
    glPopMatrix()


def update_player_movement():
    """
    Handles player movement physics including:
    - Horizontal movement with smooth transitions
    - Jump physics with gravity
    - Speed control system with acceleration/deceleration
    """
    global player_x, player_z, player_velocity_x, player_speed
    global is_jumping, jump_velocity, is_sliding
    
    # SPEED CONTROL SYSTEM - Gradual acceleration
    if player_speed < max_speed:
        player_speed += acceleration
    
    # Horizontal movement with smooth velocity
    player_x += player_velocity_x
    player_velocity_x *= 0.85  # Smooth deceleration
    
    # Keep player within road boundaries (-200 to 200)
    if player_x < -200:
        player_x = -200
    if player_x > 200:
        player_x = 200
    
    # JUMP PHYSICS
    if is_jumping:
        player_z += jump_velocity
        jump_velocity += gravity  # Apply gravity
        
        # Land on ground
        if player_z <= ground_level:
            player_z = ground_level
            is_jumping = False
            jump_velocity = 0
            is_sliding = False


def handle_collision():
    """
    Called when player hits an obstacle.
    Reduces speed as part of the speed control system.
    """
    global player_speed
    player_speed = max(base_speed, player_speed - deceleration)


def keyboardListener(key, x, y):
    """
    Handles keyboard inputs for player movement controls.
    - A/D: Move left/right
    - W: Jump
    - S: Slide
    """
    global player_velocity_x, is_jumping, jump_velocity, is_sliding
    
    # Move LEFT (A key)
    if key == b'a':
        player_velocity_x = -8
    
    # Move RIGHT (D key)
    if key == b'd':
        player_velocity_x = 8
    
    # JUMP (W key)
    if key == b'w' and not is_jumping:
        is_jumping = True
        jump_velocity = jump_strength
    
    # SLIDE (S key)
    if key == b's' and not is_jumping:
        is_sliding = True
    
    # Test collision (space bar for testing)
    if key == b' ':
        handle_collision()
    
    glutPostRedisplay()


def specialKeyListener(key, x, y):
    """
    Handles special key inputs for camera control.
    """
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


def mouseListener(button, state, x, y):
    """
    Mouse input handler (not used in this feature set).
    """
    pass


def draw_text(x, y, text, font=None):
    """
    Draws 2D text on screen at specified coordinates.
    """
    if font is None:
        font = GLUT_BITMAP_9_BY_15
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
        glutBitmapCharacter(font, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def setupCamera():
    """
    Configures the camera's projection and view settings.
    """
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
    """
    Continuous update function.
    """
    update_player_movement()
    glutPostRedisplay()


def showScreen():
    """
    Main display function - renders the entire scene.
    """
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    setupCamera()
    
    # Draw the road/grid
    glBegin(GL_QUADS)
    glColor3f(0.3, 0.3, 0.3)  # Dark gray road
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glEnd()
    
    # Draw lane markers
    glColor3f(1, 1, 0)
    glBegin(GL_LINES)
    glVertex3f(-100, GRID_LENGTH, 1)
    glVertex3f(-100, -GRID_LENGTH, 1)
    glVertex3f(100, GRID_LENGTH, 1)
    glVertex3f(100, -GRID_LENGTH, 1)
    glEnd()
    
    # Draw the skateboard character
    draw_skateboard_character()
    
    # Display game info
    draw_text(10, 770, f"Speed: {player_speed:.1f} | Max Speed: {max_speed}")
    draw_text(10, 740, f"Position: {player_x:.0f} | Height: {player_z:.0f}")
    draw_text(10, 710, f"Controls: A/D - Move | W - Jump | S - Slide | Space - Test Collision")
    
    if is_jumping:
        draw_text(10, 680, "JUMPING!")
    if is_sliding:
        draw_text(10, 680, "SLIDING!")
    
    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Skateboard Game - Player Control (Naimur)")
    
    glEnable(GL_DEPTH_TEST)  # Enable depth testing for 3D rendering
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    glutMainLoop()


if __name__ == "__main__":
    main()