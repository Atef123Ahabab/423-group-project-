"""
NAIMUR - Player & Character Control Module
Features:
1. Skateboard Character Design & Animation
2. Player Movement Controls (Left/Right, Jump, Slide)
3. Speed Control System (Acceleration & Deceleration)
"""

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# ============================================================================
# RENDERING MODE CONTROL
# ============================================================================
# Can switch between 2D and 3D rendering
USE_3D_MODE = False  # Set to True for 3D OpenGL rendering, False for 2D

# ============================================================================
# CAMERA VARIABLES (For 3D Mode)
# ============================================================================
camera_pos = (0, 500, 500)
camera_field_of_view = 120
GRID_LENGTH = 600

# ============================================================================
# PLAYER CHARACTER VARIABLES
# ============================================================================

# Player position and movement (2D mode)
player_x_2d = 550.0  # Horizontal position (left/right on road)
player_y_2d = 150.0  # Vertical position (jumping)
player_base_y = 150.0
ground_y = 150.0  # Ground level for 2D mode
player_lane = 1  # 0=left-inner, 1=center-left, 2=center-right, 3=right-inner (4 lanes)
lanes_2d = [450, 550, 650, 750]  # 4 centered lanes

# Window dimensions (for 2D mode)
window_width = 1200
window_height = 800

# Player position (3D mode)
player_x = -50  # Horizontal position (-200 to 200 range for 4 lanes)
player_y = -400  # Fixed forward position
player_z = 30  # Height above ground
lanes_3d = [-150, -50, 50, 150]  # 4 lanes for 3D mode

# Movement states
player_velocity_x = 0  # Horizontal velocity
player_velocity_y = 0  # Vertical velocity (for jumping in 2D)
player_is_jumping = False
player_is_sliding = False

# Speed control system
player_speed = 2.0  # Forward speed (increases over time)
base_speed = 2.0  # Starting speed
max_speed = 15.0  # Maximum speed
acceleration = 0.02  # Speed increase rate
speed_increment = 0.02  # Same as acceleration (for compatibility)
deceleration = 0.5  # Speed reduction on collision
speed_increase_timer = 0  # Timer for speed increases

# Sliding mechanics
slide_duration = 0
slide_duration_frames = 30

# Lane system
current_lane = 1  # 4-lane system (0=left, 1=center-left, 2=center-right, 3=right)

# Jump mechanics
jump_velocity = 0
gravity_3d = -1.5
gravity_2d = -1.2  # Gravity pulls down (negative acceleration)
jump_strength_3d = 20
jump_strength_2d = 18  # Initial upward velocity when jumping
ground_level = 30

# Animation variables
animation_frame = 0
leg_swing = 0
arm_swing = 0
body_tilt = 0
leg_angle = 0
arm_angle = 0

# Character dimensions
player_width = 30
player_height = 40

# ============================================================================
# UTILITY DRAWING FUNCTIONS (For 2D Mode)
# ============================================================================

def draw_filled_rect(x, y, w, h):
    """Draw filled rectangle using triangles (2D mode)"""
    glBegin(GL_TRIANGLES)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x, y + h)
    
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()

def draw_circle_2d(cx, cy, radius, filled=True):
    """Draw circle using triangles (2D mode)"""
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

# ============================================================================
# CHARACTER DRAWING - 3D VERSION
# ============================================================================

def draw_skateboard_character_3d():
    """
    FEATURE 1: Skateboard Character Design & Animation (3D Version)
    - Draws the skateboard character with all body parts in 3D
    - Includes running animation with moving legs and arms
    - Shows jumping pose when in air
    - Shows crouched sliding pose
    """
    global animation_frame, leg_swing, arm_swing, body_tilt, player_z
    global player_is_jumping, player_is_sliding, player_speed
    
    glPushMatrix()
    glTranslatef(player_x, player_y, player_z)
    
    # Calculate animation values based on speed
    if not player_is_jumping and not player_is_sliding:
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
    if player_is_sliding:
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
    if not player_is_jumping and not player_is_sliding:
        glRotatef(leg_swing, 1, 0, 0)  # Leg swing for running
    glColor3f(0.1, 0.1, 0.5)  # Dark blue pants
    glScalef(0.5, 0.5, 1.5)
    glutSolidCube(15)
    glPopMatrix()
    
    # RIGHT LEG
    glPushMatrix()
    glTranslatef(8, 0, -15)
    if not player_is_jumping and not player_is_sliding:
        glRotatef(-leg_swing, 1, 0, 0)  # Opposite leg swing
    glColor3f(0.1, 0.1, 0.5)
    glScalef(0.5, 0.5, 1.5)
    glutSolidCube(15)
    glPopMatrix()
    
    glPopMatrix()

# ============================================================================
# CHARACTER DRAWING - 2D VERSION
# ============================================================================

def draw_skateboard_character_2d():
    """
    FEATURE 1: Skateboard Character Design & Animation (2D Version)
    - Draws the skateboard character with all body parts in 2D
    - Includes running animation with moving legs and arms
    - Shows jumping pose when in air
    - Shows crouched sliding pose
    """
    global player_x_2d, player_y_2d, animation_frame
    global leg_angle, arm_angle, player_is_sliding, player_speed
    
    px = player_x_2d
    py = player_y_2d
    
    # SLIDING ANIMATION - Character crouches down
    if player_is_sliding:
        py -= 15  # Lower the character
        
        # Skateboard
        glColor3f(0.9, 0.5, 0.2)
        draw_filled_rect(px - 15, py - 5, 30, 8)
        
        # Wheels
        glColor3f(0.2, 0.2, 0.2)
        draw_circle_2d(px - 10, py - 5, 4)
        draw_circle_2d(px + 10, py - 5, 4)
        
        # Crouched body
        glColor3f(0.2, 0.6, 0.9)
        draw_filled_rect(px - 10, py + 3, 20, 15)
        
        # Head
        glColor3f(1.0, 0.8, 0.6)
        draw_circle_2d(px, py + 25, 8)
        
        # Arms extended forward (sliding pose)
        glColor3f(1.0, 0.8, 0.6)
        draw_filled_rect(px - 5, py + 10, 15, 5)
        
        return
    
    # NORMAL POSE - Standing on skateboard
    
    # Skateboard (orange/brown)
    glColor3f(0.9, 0.5, 0.2)
    draw_filled_rect(px - 15, py - 5, 30, 8)
    
    # Wheels (black)
    glColor3f(0.2, 0.2, 0.2)
    draw_circle_2d(px - 10, py - 5, 4)
    draw_circle_2d(px + 10, py - 5, 4)
    
    # ANIMATED LEGS - Move based on animation frame
    glColor3f(0.3, 0.3, 0.8)  # Blue pants
    leg_offset = math.sin(animation_frame * 0.2) * 3
    # Left leg
    draw_filled_rect(px - 10, py + 3, 6, 15 + leg_offset)
    # Right leg
    draw_filled_rect(px + 4, py + 3, 6, 15 - leg_offset)
    
    # Body/Torso
    glColor3f(0.2, 0.6, 0.9)  # Light blue shirt
    draw_filled_rect(px - 10, py + 18, 20, 18)
    
    # Head (skin color)
    glColor3f(1.0, 0.8, 0.6)
    draw_circle_2d(px, py + 45, 8)
    
    # Helmet (red)
    glColor3f(0.9, 0.1, 0.1)
    draw_circle_2d(px, py + 48, 9, filled=False)  # Helmet outline
    draw_filled_rect(px - 9, py + 45, 18, 5)  # Helmet visor
    
    # ANIMATED ARMS - Move based on animation frame
    glColor3f(1.0, 0.8, 0.6)  # Skin color
    arm_offset = math.sin(animation_frame * 0.2) * 2
    # Left arm
    draw_filled_rect(px - 15, py + 25 + arm_offset, 5, 12)
    # Right arm
    draw_filled_rect(px + 10, py + 25 - arm_offset, 5, 12)

def draw_skateboard_character():
    """Main character drawing function - switches between 2D and 3D"""
    if USE_3D_MODE:
        draw_skateboard_character_3d()
    else:
        draw_skateboard_character_2d()

# ============================================================================
# MOVEMENT UPDATE - DUAL MODE
# ============================================================================

def update_player_movement():
    """
    Main movement update - handles both 2D and 3D modes
    Includes:
    - Horizontal lane switching
    - Vertical movement (jumping/falling/gravity)
    - Speed control system
    """
    if USE_3D_MODE:
        # 3D MODE MOVEMENT
        global player_x, player_z, player_velocity_x, player_speed
        global is_jumping, jump_velocity, is_sliding
        
        # SPEED CONTROL SYSTEM
        if player_speed < max_speed:
            player_speed += acceleration
        
        # Horizontal movement
        player_x += player_velocity_x
        player_velocity_x *= 0.85  # Smooth deceleration
        
        # Keep within road boundaries
        if player_x < -200:
            player_x = -200
        if player_x > 200:
            player_x = 200
        
        # JUMP PHYSICS
        if is_jumping:
            player_z += jump_velocity
            jump_velocity += gravity
            
            if player_z <= ground_level:
                player_z = ground_level
                is_jumping = False
                jump_velocity = 0
                is_sliding = False
    else:
        # 2D MODE MOVEMENT
        global player_x_2d, player_y_2d, player_velocity_y, player_is_jumping
        global player_is_sliding, slide_duration, animation_frame
        
        # SPEED CONTROL SYSTEM
        if player_speed < max_speed:
            player_speed += speed_increment
        
        # Update animation frame
        animation_frame += player_speed * 0.1
        
        # JUMP PHYSICS - Apply gravity when jumping or in air
        if player_is_jumping:
            # Apply gravity to velocity
            player_velocity_y += gravity_2d
            # Update vertical position
            player_y_2d += player_velocity_y
            
            # Check if landed on ground
            if player_y_2d <= ground_y:
                player_y_2d = ground_y
                player_velocity_y = 0
                player_is_jumping = False
        else:
            # Make sure player stays on ground when not jumping
            player_y_2d = ground_y
            player_velocity_y = 0
        
        # Update sliding
        if player_is_sliding:
            slide_duration -= 1
            if slide_duration <= 0:
                player_is_sliding = False
                slide_duration = 0


# ============================================================================
# COLLISION HANDLER
# ============================================================================

def handle_collision():
    """
    Called when player hits an obstacle.
    Reduces speed as part of the speed control system.
    """
    global player_speed
    player_speed = max(base_speed, player_speed - deceleration)

# ============================================================================
# KEYBOARD INPUT - DUAL MODE
# ============================================================================

def keyboardListener(key, x, y):
    """
    Handles keyboard inputs for player movement controls.
    Supports both 2D and 3D modes.
    - A/Left: Move left
    - D/Right: Move right
    - W/Up: Jump
    - S/Down: Slide
    """
    if USE_3D_MODE:
        # 3D MODE CONTROLS
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
        # 2D MODE CONTROLS
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

# ============================================================================
# MODULAR CONTROL FUNCTIONS (For 2D integration)
# ============================================================================

def move_left():
    """Move player to left lane"""
    global current_lane, player_x_2d
    if current_lane > 0:
        current_lane -= 1
        player_x_2d = lanes_2d[current_lane]

def move_right():
    """Move player to right lane"""
    global current_lane, player_x_2d
    if current_lane < len(lanes_2d) - 1:
        current_lane += 1
        player_x_2d = lanes_2d[current_lane]

def jump():
    """Make player jump"""
    global player_is_jumping, player_velocity_y
    if not player_is_jumping:
        player_is_jumping = True
        player_velocity_y = jump_strength_2d

def slide():
    """Make player slide"""
    global player_is_sliding, slide_duration
    if not player_is_jumping and not player_is_sliding:
        player_is_sliding = True
        slide_duration = slide_duration_frames

# ============================================================================
# GETTER/SETTER FUNCTIONS (For integration with main_game.py)
# ============================================================================

def get_player_position():
    """Returns (x, y) position of player for collision detection"""
    if USE_3D_MODE:
        return (player_x, player_z)
    else:
        return (player_x_2d, player_y_2d)

def get_player_lane():
    """Returns current lane index (0, 1, or 2)"""
    return current_lane

def get_player_speed():
    """Returns current player speed"""
    return player_speed

def set_player_speed(new_speed):
    """Sets player speed (used after collisions)"""
    global player_speed
    player_speed = max(base_speed, min(new_speed, max_speed))

def is_player_jumping():
    """Returns True if player is in the air"""
    if USE_3D_MODE:
        return is_jumping
    else:
        return player_is_jumping

def is_player_sliding():
    """Returns True if player is sliding"""
    if USE_3D_MODE:
        return is_sliding
    else:
        return player_is_sliding

def reset_player():
    """Reset player to starting position and state"""
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
        current_lane = 1  # Middle lane
        player_x_2d = lanes_2d[current_lane]
        player_y_2d = ground_y
        player_velocity_y = 0
        player_is_jumping = False
        player_is_sliding = False
    
    player_speed = base_speed
    animation_frame = 0

def get_character_width():
    """Returns character width for collision detection"""
    return 30 if not player_is_sliding else 35

def get_character_height():
    """Returns character height for collision detection"""
    return 55 if not player_is_sliding else 25


# ============================================================================
# SPECIAL KEY AND MOUSE LISTENERS (3D Mode Only)
# ============================================================================

def specialKeyListener(key, x, y):
    """
    Handles special key inputs for camera control (3D mode).
    Arrow keys control camera position.
    """
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
    """Mouse input handler (not used in current features)"""
    pass

# ============================================================================
# RENDERING FUNCTIONS
# ============================================================================

def draw_text(x, y, text, font=None):
    """
    Draws 2D text on screen at specified coordinates.
    Used for displaying game information.
    """
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
    """
    Configures the camera's projection and view settings.
    Sets up perspective projection and lookAt position.
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
    Continuous update function called by GLUT.
    Updates movement and triggers redisplay.
    """
    update_player_movement()
    glutPostRedisplay()

def showScreen():
    """
    Main display function - renders the entire scene.
    Draws the skateboard character and game environment.
    """
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    if USE_3D_MODE:
        # 3D MODE RENDERING
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
        
        # Draw the character
        draw_skateboard_character()
        
        # Display game info
        draw_text(10, 770, f"Speed: {player_speed:.1f} | Max Speed: {max_speed}")
        draw_text(10, 740, f"Position: {player_x:.0f} | Height: {player_z:.0f}")
        draw_text(10, 710, f"Controls: A/D - Move | W - Jump | S - Slide | Space - Test Collision")
        
        if is_jumping:
            draw_text(10, 680, "JUMPING!")
        if is_sliding:
            draw_text(10, 680, "SLIDING!")
    else:
        # 2D MODE RENDERING (Simpler, for integration)
        # Set up 2D projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, window_width, 0, window_height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Draw simple background
        glColor3f(0.2, 0.2, 0.3)
        draw_filled_rect(0, 0, window_width, window_height)
        
        # Draw ground
        glColor3f(0.3, 0.3, 0.3)
        draw_filled_rect(0, 0, window_width, ground_y + 10)
        
        # Draw lane dividers
        glColor3f(1, 1, 0)
        for lane_x in lanes_2d:
            draw_filled_rect(lane_x - 2, 0, 4, window_height)
        
        # Draw the character
        draw_skateboard_character()
        
        # Display info
        draw_text(10, window_height - 30, 
                 f"Speed: {player_speed:.1f} | Lane: {current_lane + 1}/3")
    
    glutSwapBuffers()

# ============================================================================
# INITIALIZATION & MAIN (For Standalone 3D Mode)
# ============================================================================

def init():
    """Initialize OpenGL settings"""
    glClearColor(0.53, 0.81, 0.92, 1.0)  # Sky blue background
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)

def main():
    """
    Main function to run the standalone demo.
    Only runs if this file is executed directly (not imported).
    """
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

# Only run standalone if this file is executed directly
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
    # Module imported - functions available for use
    print(f"[Naimur Module] Loaded in {'3D' if USE_3D_MODE else '2D'} mode")