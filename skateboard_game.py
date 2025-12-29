from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# ============================================================================
# GAME CONFIGURATION
# ============================================================================
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800

# Camera settings
camera_pos = (0, 500, 500)
camera_field_of_view = 120
GRID_LENGTH = 600

# ============================================================================
# NAIMUR'S FEATURES: PLAYER & CHARACTER CONTROL
# ============================================================================

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

# ============================================================================
# SAMI'S FEATURES: OBSTACLES & COLLISION HANDLING
# ============================================================================

# Game state
lives = 3
score = 0
game_over = False

# Obstacle and life token lists
obstacles = []  # List of dictionaries: {'x': x, 'y': y, 'z': z, 'type': 'box'/'barrier'}
life_tokens = []  # List of dictionaries: {'x': x, 'y': y, 'z': z}

# Spawn control
obstacle_spawn_timer = 0
token_spawn_timer = 0
obstacle_spawn_interval = 60  # Frames between spawns
token_spawn_interval = 200


# ============================================================================
# NAIMUR'S FEATURE 1: SKATEBOARD CHARACTER DESIGN & ANIMATION
# ============================================================================
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


# ============================================================================
# NAIMUR'S FEATURE 2: PLAYER MOVEMENT CONTROLS
# ============================================================================
def keyboardListener(key, x, y):
    """
    Handles keyboard inputs for player movement controls.
    - A/D: Move left/right
    - W: Jump
    - S: Slide
    - R: Restart game
    """
    global player_velocity_x, is_jumping, jump_velocity, is_sliding, game_over
    global lives, score, obstacles, life_tokens, player_speed
    
    # Restart game
    if key == b'r' and game_over:
        game_over = False
        lives = 3
        score = 0
        obstacles.clear()
        life_tokens.clear()
        player_speed = base_speed
        return
    
    if game_over:
        return
    
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


# ============================================================================
# NAIMUR'S FEATURE 3: SPEED CONTROL SYSTEM (ACCELERATION & DECELERATION)
# ============================================================================
def update_player_movement():
    """
    Handles player movement physics including:
    - Horizontal movement with smooth transitions
    - Jump physics with gravity
    - Speed control system with acceleration/deceleration
    """
    global player_x, player_z, player_velocity_x, player_speed
    global is_jumping, jump_velocity, is_sliding
    
    if game_over:
        return
    
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


# ============================================================================
# SAMI'S FEATURE 1: OBSTACLE GENERATION
# ============================================================================
def spawn_obstacles():
    """
    Regular spawning of obstacles such as boxes and barriers on the road.
    Obstacles spawn at regular intervals and in different lanes.
    """
    global obstacle_spawn_timer, obstacles
    
    if game_over:
        return
    
    obstacle_spawn_timer += 1
    
    if obstacle_spawn_timer >= obstacle_spawn_interval:
        obstacle_spawn_timer = 0
        
        # Randomly choose lane (-100, 0, or 100 for 3 lanes)
        lane_positions = [-100, 0, 100]
        x_pos = random.choice(lane_positions)
        
        # Randomly choose obstacle type
        obs_type = random.choice(['box', 'barrier'])
        
        # Spawn obstacle in front of player
        obstacles.append({
            'x': x_pos,
            'y': player_y + 800,  # Spawn ahead
            'z': 40,
            'type': obs_type
        })


def draw_obstacles():
    """
    Draws obstacles (boxes and barriers) on the road.
    """
    for obs in obstacles:
        glPushMatrix()
        glTranslatef(obs['x'], obs['y'], obs['z'])
        
        if obs['type'] == 'box':
            # Draw box obstacle (orange/yellow)
            glColor3f(0.9, 0.6, 0.1)
            glutSolidCube(50)
        else:  # barrier
            # Draw barrier obstacle (red and white stripes)
            glColor3f(0.9, 0.1, 0.1)
            glScalef(2, 0.3, 1)
            glutSolidCube(50)
        
        glPopMatrix()


def update_obstacles():
    """
    Moves obstacles toward the player and removes off-screen obstacles.
    """
    global obstacles, score
    
    if game_over:
        return
    
    for obs in obstacles[:]:
        # Move obstacle toward player
        obs['y'] -= player_speed * 3
        
        # Remove obstacles that went past the player
        if obs['y'] < player_y - 200:
            obstacles.remove(obs)
            score += 10  # Award points for dodging


# ============================================================================
# SAMI'S FEATURE 2: COLLISION DETECTION
# ============================================================================
def check_collisions():
    """
    Detection of collisions between the player and obstacles.
    Triggers life loss when a collision occurs.
    """
    global lives, game_over, obstacles
    
    if game_over:
        return
    
    # Define player hitbox
    player_size = 30
    player_height = 60
    
    for obs in obstacles[:]:
        # Calculate distance between player and obstacle
        dx = abs(player_x - obs['x'])
        dy = abs(player_y - obs['y'])
        dz = abs(player_z - obs['z'])
        
        # Check collision (simple bounding box collision)
        if dx < 40 and dy < 40 and dz < 40:
            # Collision detected!
            lives -= 1
            obstacles.remove(obs)
            handle_collision()  # Reduce speed
            
            # Check game over
            if lives <= 0:
                game_over = True


# ============================================================================
# SAMI'S FEATURE 3: LIFE TOKENS (HEALTH PICKUP)
# ============================================================================
def spawn_life_tokens():
    """
    Special collectibles that appear on the road.
    Spawn less frequently than obstacles.
    """
    global token_spawn_timer, life_tokens
    
    if game_over:
        return
    
    token_spawn_timer += 1
    
    if token_spawn_timer >= token_spawn_interval:
        token_spawn_timer = 0
        
        # Randomly choose lane
        lane_positions = [-100, 0, 100]
        x_pos = random.choice(lane_positions)
        
        # Spawn life token
        life_tokens.append({
            'x': x_pos,
            'y': player_y + 900,
            'z': 30
        })


def draw_life_tokens():
    """
    Draws life tokens (green hearts/spheres) on the road.
    """
    for token in life_tokens:
        glPushMatrix()
        glTranslatef(token['x'], token['y'], token['z'])
        
        # Draw rotating green heart (sphere for simplicity)
        glColor3f(0.1, 0.9, 0.1)
        glutSolidSphere(15, 12, 12)
        
        # Add a glow effect with a slightly transparent outer sphere
        glColor4f(0.3, 1.0, 0.3, 0.5)
        glutWireSphere(18, 8, 8)
        
        glPopMatrix()


def update_life_tokens():
    """
    Moves life tokens and checks for collection.
    Restores one lost life when collected.
    """
    global life_tokens, lives
    
    if game_over:
        return
    
    for token in life_tokens[:]:
        # Move token toward player
        token['y'] -= player_speed * 3
        
        # Check collection
        dx = abs(player_x - token['x'])
        dy = abs(player_y - token['y'])
        dz = abs(player_z - token['z'])
        
        if dx < 30 and dy < 30 and dz < 30:
            # Collected!
            lives += 1
            life_tokens.remove(token)
        
        # Remove tokens that went past the player
        elif token['y'] < player_y - 200:
            life_tokens.remove(token)


# ============================================================================
# RENDERING & DISPLAY
# ============================================================================
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
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    
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


def showScreen():
    """
    Main display function - renders the entire scene.
    """
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    
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
    
    # Draw game objects
    draw_obstacles()  # Sami's Feature 1
    draw_life_tokens()  # Sami's Feature 3
    draw_skateboard_character()  # Naimur's Feature 1
    
    # Display game info
    draw_text(10, 770, f"SKATEBOARD ENDLESS RUNNER - Naimur & Sami")
    draw_text(10, 740, f"Lives: {lives} | Score: {score} | Speed: {player_speed:.1f}")
    draw_text(10, 710, f"Controls: A/D - Move | W - Jump | S - Slide")
    
    if is_jumping:
        draw_text(10, 680, "JUMPING!")
    if is_sliding:
        draw_text(10, 680, "SLIDING!")
    
    if game_over:
        draw_text(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2, "GAME OVER!")
        draw_text(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 30, f"Final Score: {score}")
        draw_text(WINDOW_WIDTH//2 - 120, WINDOW_HEIGHT//2 - 60, "Press R to Restart")
    
    glutSwapBuffers()


def idle():
    """
    Continuous update function - handles all game updates.
    """
    # Naimur's updates
    update_player_movement()  # Feature 3: Speed control & movement
    
    # Sami's updates
    spawn_obstacles()  # Feature 1: Obstacle generation
    update_obstacles()
    spawn_life_tokens()  # Feature 3: Life token generation
    update_life_tokens()
    check_collisions()  # Feature 2: Collision detection
    
    glutPostRedisplay()


def mouseListener(button, state, x, y):
    """
    Mouse input handler (not used in this game).
    """
    pass


# ============================================================================
# MAIN FUNCTION
# ============================================================================
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Skateboard Endless Runner - Naimur & Sami")
    
    glEnable(GL_DEPTH_TEST)  # Enable depth testing for 3D rendering
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    glutMainLoop()


if __name__ == "__main__":
    main()
