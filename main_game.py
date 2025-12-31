"""
============================================================================
CSE423 - SKATEBOARD ENDLESS RUNNER GAME
PREHISTORIC THEME: STONE AGE / JURASSIC ERA
============================================================================
Group Project - Complete Integration of All 4 Member Modules

TEAM MEMBERS & FEATURES:
------------------------
NAIMUR - Player & Character Control (3 Features):
  1. Skateboard Character Design & Animation
  2. Player Movement Controls (WASD/Arrows)
  3. Speed Control System (Acceleration & Deceleration)

SAMI - Obstacles & Collision Handling (3 Features):
  1. Obstacle Generation (Boxes, Barriers, Cones)
  2. Collision Detection System
  3. Life Tokens (Health Pickups)

TITHI - Scoring & Game Flow (4 Features):
  1. Distance-Based Score Increment
  2. Level Progression System
  3. Score-Based Difficulty Feedback
  4. Score Multiplier Zone System

ATEF - Game State & Environment (4 Features):
  1. Dynamic Camera System (Camera Transitions & Shake)
  2. Game State Initialization & Reset Logic
  3. Difficulty Scaling System
  4. Prehistoric Background & Environment (Parallax, Animated)

============================================================================
"""

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

# Import all team member modules
import naimur
import sami
import tithi

# ============================================================================
# WINDOW CONFIGURATION
# ============================================================================
W_WIDTH, W_HEIGHT = 1200, 800

# ============================================================================
# GAME STATE (ATEF'S FEATURE 2: Game State Management)
# ============================================================================
game_state = "playing"  # "playing", "paused", "game_over"
game_time = 0

# ============================================================================
# ATEF'S FEATURES: Camera & Environment
# ============================================================================
# ATEF FEATURE 1: Dynamic Camera System
camera_shake = 0
camera_zoom = 1.0
camera_y_offset = 0
camera_transition = 0.0
camera_mode = "third_person"  # "third_person", "first_person"

# ATEF FEATURE 4: Prehistoric Background & Environment
background_offset = 0
weather_effect = "clear"  # "clear", "dust", "volcano"
time_period = "prehistoric"

# Prehistoric parallax layers (mountains, volcanoes, dinosaurs)
bg_layers = [
    {"offset": 0, "speed": 0.15, "type": "mountains_far"},
    {"offset": 0, "speed": 0.35, "type": "volcano"},
    {"offset": 0, "speed": 0.6, "type": "mountains_near"},
]

# Dinosaur background elements
dinosaurs = []
pterodactyls = []
volcano_particles = []

# ============================================================================
# ATEF FEATURE 4: PREHISTORIC BACKGROUND DRAWING
# ============================================================================

def draw_filled_rect(x, y, w, h):
    """Draw filled rectangle using triangles"""
    glBegin(GL_TRIANGLES)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x, y + h)
    
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()

def draw_circle(cx, cy, radius):
    """Draw circle"""
    num_segments = 20
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx, cy)
    for i in range(num_segments + 1):
        angle = 2.0 * math.pi * i / num_segments
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        glVertex2f(x, y)
    glEnd()

def draw_triangle(x1, y1, x2, y2, x3, y3):
    """Draw filled triangle"""
    glBegin(GL_TRIANGLES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glVertex2f(x3, y3)
    glEnd()

def draw_prehistoric_background():
    """
    ATEF FEATURE 4: Prehistoric/Jurassic Background
    - Layered mountains with parallax
    - Volcano with smoke
    - Dinosaur silhouettes
    - Stone age aesthetic
    """
    global bg_layers, background_offset
    
    # Sky - Orange/red prehistoric sky
    glColor3f(0.8, 0.5, 0.3)  # Warm orange sky
    draw_filled_rect(0, 0, W_WIDTH, W_HEIGHT)
    
    # Sun/Moon (prehistoric celestial body)
    glColor3f(0.95, 0.8, 0.5)  # Yellowish sun
    draw_circle(1000, 650, 60)
    
    # Far mountains layer (darkest)
    layer = bg_layers[0]
    glColor3f(0.3, 0.25, 0.2)  # Dark brown
    y_offset = -layer["offset"] % 800
    for i in range(3):
        base_y = i * 300 - y_offset
        # Jagged mountain peaks
        for j in range(5):
            x = j * 250 + 50
            draw_triangle(x, base_y, x + 100, base_y + 200, x + 200, base_y)
    
    # Volcano layer (middle)
    layer = bg_layers[1]
    glColor3f(0.4, 0.3, 0.25)  # Brown volcano
    y_offset = -layer["offset"] % 800
    volcano_x = W_WIDTH - 300
    volcano_y = 100 - (y_offset % 200)
    # Volcano shape
    draw_triangle(volcano_x - 100, volcano_y, volcano_x, volcano_y + 250, volcano_x + 100, volcano_y)
    
    # Volcano crater
    glColor3f(0.9, 0.3, 0.1)  # Red hot lava
    draw_triangle(volcano_x - 30, volcano_y + 250, volcano_x, volcano_y + 280, volcano_x + 30, volcano_y + 250)
    
    # Volcano smoke
    glColor3f(0.5, 0.5, 0.5)  # Gray smoke
    smoke_offset = int(background_offset * 0.3)
    for i in range(3):
        smoke_y = volcano_y + 280 + i * 40 + (smoke_offset % 50)
        if smoke_y < W_HEIGHT:
            draw_circle(volcano_x + random.randint(-20, 20), smoke_y, 30 - i * 5)
    
    # Near mountains layer (lightest)
    layer = bg_layers[2]
    glColor3f(0.5, 0.4, 0.3)  # Lighter brown
    y_offset = -layer["offset"] % 800
    for i in range(2):
        base_y = i * 400 - y_offset
        for j in range(4):
            x = j * 300
            draw_triangle(x, base_y, x + 120, base_y + 150, x + 240, base_y)
    
    # Pterodactyl silhouettes (flying dinosaurs)
    glColor3f(0.2, 0.15, 0.1)  # Dark silhouette
    ptero_offset = int(background_offset * 0.5) % W_WIDTH
    for i in range(2):
        x = (ptero_offset + i * 500) % W_WIDTH
        y = 500 + i * 100
        # Simple pterodactyl shape
        draw_triangle(x, y, x + 30, y + 10, x + 20, y - 10)  # Body
        draw_triangle(x - 20, y + 5, x, y, x + 10, y + 15)  # Left wing
        draw_triangle(x + 20, y + 5, x + 50, y + 15, x + 30, y)  # Right wing

def draw_prehistoric_road():
    """
    Draw the stone age road with rock textures - CENTERED 4-LANE ROAD
    Road spans from x=400 to x=800 (400px wide, centered in 1200px window)
    """
    global background_offset
    
    # Stone/dirt road surface (centered)
    glColor3f(0.4, 0.35, 0.25)  # Brown dirt road
    draw_filled_rect(400, 0, 400, W_HEIGHT)  # Centered 400px wide road
    
    # Rock textures on road
    glColor3f(0.35, 0.3, 0.2)  # Darker rocks
    rock_offset = int(background_offset) % 100
    for y in range(-rock_offset, W_HEIGHT, 100):
        for x in [420, 500, 580, 660, 740, 780]:  # Spread across 4 lanes
            if random.randint(0, 2) == 0:
                draw_circle(x + random.randint(-10, 10), y + random.randint(0, 50), random.randint(5, 12))
    
    # Cave paintings on road edges (lane markings for 4 lanes)
    glColor3f(0.6, 0.5, 0.4)  # Light stone color
    lane_offset = int(background_offset) % 80
    for y in range(-lane_offset, W_HEIGHT, 80):
        # Primitive symbols instead of lane lines (3 markers for 4 lanes)
        # Lane marker 1 (between lane 0 and 1)
        draw_filled_rect(495, y, 10, 30)
        # Lane marker 2 (between lane 1 and 2)
        draw_filled_rect(595, y, 10, 30)
        # Lane marker 3 (between lane 2 and 3)
        draw_filled_rect(695, y, 10, 30)
    
    # Road edges - stone borders
    glColor3f(0.5, 0.45, 0.35)  # Stone color
    draw_filled_rect(395, 0, 10, W_HEIGHT)  # Left edge
    draw_filled_rect(795, 0, 10, W_HEIGHT)  # Right edge
    
    # Add some bones on the road edges (centered road)
    glColor3f(0.9, 0.85, 0.8)  # Bone white
    bone_offset = int(background_offset * 0.7) % 150
    for y in range(-bone_offset, W_HEIGHT, 150):
        # Left side bones (before road starts)
        draw_filled_rect(350, y, 20, 8)
        draw_circle(348, y + 4, 6)
        draw_circle(372, y + 4, 6)
        # Right side bones (after road ends)
        draw_filled_rect(820, y + 50, 20, 8)
        draw_circle(818, y + 54, 6)
        draw_circle(842, y + 54, 6)

def draw_weather_effects():
    """
    ATEF FEATURE 4: Prehistoric Weather Effects
    - Dust storms
    - Volcanic ash
    """
    global weather_effect, background_offset
    
    if weather_effect == "dust":
        # Dust particles
        glColor3f(0.7, 0.6, 0.5)
        for i in range(40):
            x = (random.randint(0, W_WIDTH) + int(background_offset * 2)) % W_WIDTH
            y = random.randint(0, W_HEIGHT)
            draw_circle(x, y, 3)
    
    elif weather_effect == "volcano":
        # Volcanic ash falling
        glColor3f(0.3, 0.3, 0.3)
        for i in range(30):
            x = random.randint(0, W_WIDTH)
            y = (random.randint(0, W_HEIGHT) + int(background_offset * 3)) % W_HEIGHT
            draw_circle(x, y, 4)

# ============================================================================
# ATEF FEATURE 1: DYNAMIC CAMERA SYSTEM
# ============================================================================

def trigger_camera_shake(intensity):
    """ATEF FEATURE 1: Camera Shake Effect"""
    global camera_shake
    camera_shake = intensity

def apply_camera_shake():
    """Apply camera shake effect"""
    global camera_shake
    if camera_shake > 0:
        shake_x = random.randint(-5, 5) * (camera_shake / 10.0)
        shake_y = random.randint(-5, 5) * (camera_shake / 10.0)
        glTranslatef(shake_x, shake_y, 0)
        camera_shake -= 1

def setup_camera_view(player_x, player_y, player_speed):
    """
    ATEF FEATURE 1: Dynamic Camera Transitions
    - Switch between first-person and third-person views
    """
    global camera_mode, camera_y_offset, camera_transition, camera_zoom
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    
    zoom_factor = camera_zoom
    
    if camera_mode == "first_person":
        camera_transition = min(camera_transition + 0.05, 1.0)
        target_y_offset = -200 * camera_transition
        camera_y_offset += (target_y_offset - camera_y_offset) * 0.1
        zoom_factor = 1.1 + (0.2 * camera_transition)
        
        glOrtho(-W_WIDTH * 0.1 * zoom_factor, 
                W_WIDTH * (1 + 0.1 * zoom_factor), 
                camera_y_offset * zoom_factor, 
                W_HEIGHT + camera_y_offset * zoom_factor, 
                -1, 1)
    else:
        camera_transition = max(camera_transition - 0.05, 0.0)
        target_y_offset = 0
        camera_y_offset += (target_y_offset - camera_y_offset) * 0.1
        zoom_factor = 1.0
        glOrtho(0, W_WIDTH, 0, W_HEIGHT, -1, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def toggle_camera_mode():
    """Toggle between camera views"""
    global camera_mode
    if camera_mode == "third_person":
        camera_mode = "first_person"
        print("\n>>> FIRST PERSON VIEW ACTIVATED <<<")
    else:
        camera_mode = "third_person"
        print("\n>>> THIRD PERSON VIEW ACTIVATED <<<")

# ============================================================================
# ATEF FEATURE 4: BACKGROUND UPDATE
# ============================================================================

def update_background(player_speed):
    """Update parallax background layers"""
    global bg_layers, background_offset
    
    background_offset += player_speed
    
    for layer in bg_layers:
        layer["offset"] += player_speed * layer["speed"]
        if layer["offset"] > 800:
            layer["offset"] = 0

def update_environment_based_on_score(score):
    """Change environment based on score"""
    global weather_effect
    
    if score > 500 and score < 1000:
        weather_effect = "dust"
    elif score > 1000:
        weather_effect = "volcano"
    else:
        weather_effect = "clear"

# ============================================================================
# ATEF FEATURE 3: DIFFICULTY SCALING
# ============================================================================

def scale_difficulty_with_score(score, level):
    """Calculate obstacle spawn rate based on difficulty"""
    obstacle_spawn_rate = max(30, 60 - level * 5)
    sami.set_obstacle_spawn_rate(obstacle_spawn_rate)
    return obstacle_spawn_rate

# ============================================================================
# ATEF FEATURE 2: GAME STATE MANAGEMENT
# ============================================================================

def reset_game_state():
    """Reset all game systems"""
    global game_state, game_time, camera_shake, camera_zoom
    global background_offset, weather_effect, bg_layers
    
    game_state = "playing"
    game_time = 0
    camera_shake = 0
    camera_zoom = 1.0
    background_offset = 0
    weather_effect = "clear"
    
    for layer in bg_layers:
        layer["offset"] = 0
    
    # Reset all modules
    naimur.reset_player()
    sami.reset_game()
    tithi.reset_scoring()
    
    print("=" * 60)
    print("GAME RESET - All systems reinitialized!")
    print("=" * 60)

# ============================================================================
# UI & HUD DISPLAY
# ============================================================================

def draw_text(x, y, text):
    """Draw text on screen"""
    try:
        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    except:
        pass

def draw_hud():
    """Draw game HUD"""
    # Score (from Tithi)
    tithi.draw_score_hud(500, 750)
    
    # Level (from Tithi)
    tithi.draw_level_hud(500, 720)
    
    # Speed (from Naimur)
    glColor3f(1.0, 1.0, 1.0)
    player_speed = naimur.get_player_speed()
    draw_text(500, 690, f"Speed: {player_speed:.1f}")
    
    # Lives - Draw hearts (from Sami)
    lives = sami.get_lives()
    for i in range(lives):
        x = 500 + i * 30
        y = 650
        glColor3f(1.0, 0.2, 0.2)
        draw_circle(x - 3, y + 5, 5)
        draw_circle(x + 3, y + 5, 5)
        draw_triangle(x, y - 5, x - 7, y + 3, x + 7, y + 3)
    
    # Instructions
    glColor3f(0.9, 0.9, 0.7)
    draw_text(20, 750, "PREHISTORIC RUNNER")
    draw_text(20, 720, "Arrows: Move")
    draw_text(20, 690, "Space: Jump")
    draw_text(20, 660, "Down: Slide")
    draw_text(20, 630, "P: Pause | R: Restart")
    draw_text(20, 600, "C/V: Camera")
    
    # Camera mode indicator
    if camera_mode == "first_person":
        glColor3f(0.0, 1.0, 0.0)
        draw_text(20, 560, "VIEW: 1st Person")
    else:
        glColor3f(0.5, 0.5, 1.0)
        draw_text(20, 560, "VIEW: 3rd Person")
    
    # Zone multiplier indicator (from Tithi)
    multiplier = tithi.get_zone_multiplier()
    if multiplier > 1:
        glColor3f(1.0, 0.84, 0.0)
        draw_text(500, 620, f"x{multiplier} BONUS ZONE!")

def draw_game_over():
    """Draw game over screen"""
    glColor4f(0.0, 0.0, 0.0, 0.7)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    draw_filled_rect(0, 0, W_WIDTH, W_HEIGHT)
    glDisable(GL_BLEND)
    
    glColor3f(1.0, 0.2, 0.2)
    draw_text(480, 450, "GAME OVER!")
    
    tithi.draw_game_over_stats(420, 400)
    
    glColor3f(1.0, 1.0, 1.0)
    draw_text(450, 340, "Press R to Restart")

def draw_pause_screen():
    """Draw pause overlay"""
    glColor4f(0.0, 0.0, 0.0, 0.5)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    draw_filled_rect(0, 0, W_WIDTH, W_HEIGHT)
    glDisable(GL_BLEND)
    
    glColor3f(1.0, 1.0, 0.0)
    draw_text(520, 400, "PAUSED")
    glColor3f(1.0, 1.0, 1.0)
    draw_text(470, 370, "Press P to Resume")

# ============================================================================
# MAIN GAME LOOP
# ============================================================================

def display():
    """Main display function - renders everything"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # ATEF: Setup camera
    player_x, player_y = naimur.get_player_position()
    player_speed = naimur.get_player_speed()
    setup_camera_view(player_x, player_y, player_speed)
    
    # ATEF: Apply camera shake
    apply_camera_shake()
    
    # ATEF: Draw prehistoric background
    draw_prehistoric_background()
    draw_prehistoric_road()
    
    # SAMI: Draw obstacles and tokens
    sami.draw_obstacles()
    sami.draw_life_tokens()
    
    # NAIMUR: Draw player character
    naimur.draw_skateboard_character()
    
    # ATEF: Weather effects
    draw_weather_effects()
    
    # Draw UI
    draw_hud()
    
    if game_state == "game_over":
        draw_game_over()
    elif game_state == "paused":
        draw_pause_screen()
    
    glutSwapBuffers()

def update():
    """Main update loop - integrates all modules"""
    global game_state, game_time
    
    if game_state == "playing":
        game_time += 1
        
        # Get current values
        player_speed = naimur.get_player_speed()
        score = tithi.get_score()
        level = tithi.get_level()
        
        # ATEF: Update background
        update_background(player_speed)
        
        # NAIMUR: Update player
        naimur.update_player_movement()
        
        # SAMI: Update obstacles and tokens
        sami.update_obstacles(player_speed)
        sami.update_life_tokens(player_speed)
        
        # SAMI: Check collisions
        player_x, player_y = naimur.get_player_position()
        player_width = naimur.get_character_width()
        player_height = naimur.get_character_height()
        
        # Obstacle collision
        collision = sami.handle_obstacle_collisions(player_x, player_y, player_width, player_height)
        if collision:
            trigger_camera_shake(10)
            naimur.handle_collision()
            if sami.get_lives() <= 0:
                game_state = "game_over"
        
        # Token collection
        token_collected = sami.handle_token_collection(player_x, player_y, player_width, player_height)
        if token_collected:
            trigger_camera_shake(3)
        
        # TITHI: Update score and level
        tithi.update_score(player_speed, game_state)
        tithi.update_level_progression(tithi.update_difficulty)
        
        # ATEF: Update environment
        update_environment_based_on_score(score)
        scale_difficulty_with_score(score, level)
        
        # SAMI: Spawn new obstacles
        if game_time % tithi.get_obstacle_spawn_rate_from_difficulty() == 0:
            sami.spawn_obstacle()
        
        # SAMI: Spawn life tokens
        if random.randint(0, 300) == 0:
            sami.spawn_life_token()
    
    glutPostRedisplay()

# ============================================================================
# INPUT HANDLING
# ============================================================================

def keyboard_handler(key, x, y):
    """Handle keyboard input"""
    global game_state
    
    # Reset works in all states
    if key == b'r' or key == b'R':
        reset_game_state()
        return
    
    # ESC to exit works in all states
    if key == b'\x1b':
        import sys
        sys.exit()
    
    # Pause/Resume only works when playing or paused (not in game_over)
    if key == b'p' or key == b'P':
        if game_state == "playing":
            game_state = "paused"
        elif game_state == "paused":
            game_state = "playing"
        return
    
    # Rest of controls only work during gameplay
    if game_state != "playing":
        return
    
    # Jump controls (Space or W)
    if key == b' ' or key == b'w' or key == b'W':
        naimur.jump()
    
    # Slide controls (Down arrow or S)
    if key == b's' or key == b'S':
        naimur.slide()
    
    # Left movement (A)
    if key == b'a' or key == b'A':
        naimur.move_left()
    
    # Right movement (D)
    if key == b'd' or key == b'D':
        naimur.move_right()
    
    # Camera toggle
    if key == b'c' or key == b'C' or key == b'v' or key == b'V':
        toggle_camera_mode()

def special_keyboard_handler(key, x, y):
    """Handle arrow keys (Alternative to WASD)"""
    if game_state != "playing":
        return
    
    if key == GLUT_KEY_LEFT:
        naimur.move_left()
    elif key == GLUT_KEY_RIGHT:
        naimur.move_right()
    elif key == GLUT_KEY_DOWN:
        naimur.slide()
    elif key == GLUT_KEY_UP:
        naimur.jump()

# ============================================================================
# INITIALIZATION & MAIN
# ============================================================================

def init():
    """Initialize OpenGL"""
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, W_WIDTH, 0, W_HEIGHT, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPointSize(2)

def main():
    """Main entry point"""
    glutInit()
    glutInitWindowSize(W_WIDTH, W_HEIGHT)
    glutInitWindowPosition(100, 100)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutCreateWindow(b"CSE423 Skateboard Game - Prehistoric Runner")
    
    init()
    
    glutDisplayFunc(display)
    glutIdleFunc(update)
    glutKeyboardFunc(keyboard_handler)
    glutSpecialFunc(special_keyboard_handler)
    
    print("=" * 70)
    print("      CSE423 SKATEBOARD GAME - PREHISTORIC THEME")
    print("=" * 70)
    print("\nTEAM MEMBERS & FEATURES:")
    print("-" * 70)
    print("NAIMUR - Player & Character Control")
    print("  ✓ Skateboard Character Design & Animation")
    print("  ✓ Player Movement Controls (Arrows)")
    print("  ✓ Speed Control System (Acceleration)")
    print()
    print("SAMI - Obstacles & Collision Handling")
    print("  ✓ Obstacle Generation (Box, Barrier, Cone)")
    print("  ✓ Collision Detection (AABB)")
    print("  ✓ Life Tokens (Heart Pickups)")
    print()
    print("TITHI - Scoring & Game Flow")
    print("  ✓ Distance-Based Score Increment")
    print("  ✓ Level Progression System")
    print("  ✓ Score-Based Difficulty Feedback")
    print("  ✓ Zone Multiplier System (2x Bonus)")
    print()
    print("ATEF - Game State & Environment")
    print("  ✓ Dynamic Camera System (1st/3rd Person)")
    print("  ✓ Game State & Reset Logic")
    print("  ✓ Difficulty Scaling System")
    print("  ✓ Prehistoric Background (Parallax, Volcano, Dinosaurs)")
    print("=" * 70)
    print("\nCONTROLS (Easy & User-Friendly):")
    print("  Movement:")
    print("    • A or ← (Left Arrow)   - Move Left")
    print("    • D or → (Right Arrow)  - Move Right")
    print("    • W or ↑ or Space       - Jump")
    print("    • S or ↓ (Down Arrow)   - Slide")
    print("  ")
    print("  Game Controls:")
    print("    • P              - Pause/Resume")
    print("    • R              - Restart Game")
    print("    • C or V         - Toggle Camera View")
    print("    • ESC            - Exit")
    print("=" * 70)
    print("\nOBJECTIVE:")
    print("  • Survive in the prehistoric era!")
    print("  • Avoid obstacles (rocks, barriers)")
    print("  • Collect hearts for extra lives")
    print("  • Score increases with distance")
    print("  • Watch for BONUS ZONES (2x score!)")
    print("=" * 70)
    print("\nStarting game...\n")
    
    glutMainLoop()

if __name__ == "__main__":
    main()
