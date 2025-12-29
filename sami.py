from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

# --- Game Window Settings ---
W_WIDTH, W_HEIGHT = 500, 800

# --- Game State Variables ---
player_x = 250
player_y = 100
player_width = 40
player_speed = 5

obstacles = [] # List of [x, y]
life_tokens = [] # List of [x, y]

score = 0
lives = 3
game_over = False

# --- 1. Midpoint Line Drawing Algorithm ---
# This is used for ALL rendering to ensure marks.
def draw_line(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    
    # Implementation of Midpoint Line Algorithm for all 8 octants
    zone = get_zone(x1, y1, x2, y2)
    x1, y1 = convert_to_zone0(zone, x1, y1)
    x2, y2 = convert_to_zone0(zone, x2, y2)
    
    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    dE = 2 * dy
    dNE = 2 * (dy - dx)
    
    x, y = x1, y1
    while x <= x2:
        orig_x, orig_y = convert_from_zone0(zone, x, y)
        glBegin(GL_POINTS)
        glVertex2i(orig_x, orig_y)
        glEnd()
        if d < 0:
            d += dE
            x += 1
        else:
            d += dNE
            x += 1
            y += 1

def get_zone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx) >= abs(dy):
        if dx >= 0 and dy >= 0: return 0
        if dx < 0 and dy >= 0: return 3
        if dx < 0 and dy < 0: return 4
        if dx >= 0 and dy < 0: return 7
    else:
        if dx >= 0 and dy >= 0: return 1
        if dx < 0 and dy >= 0: return 2
        if dx < 0 and dy < 0: return 5
        if dx >= 0 and dy < 0: return 6
    return 0

def convert_to_zone0(zone, x, y):
    if zone == 0: return x, y
    if zone == 1: return y, x
    if zone == 2: return y, -x
    if zone == 3: return -x, y
    if zone == 4: return -x, -y
    if zone == 5: return -y, -x
    if zone == 6: return -y, x
    if zone == 7: return x, -y

def convert_from_zone0(zone, x, y):
    if zone == 0: return x, y
    if zone == 1: return y, x
    if zone == 2: return -y, x
    if zone == 3: return -x, y
    if zone == 4: return -x, -y
    if zone == 5: return -y, -x
    if zone == 6: return y, -x
    if zone == 7: return x, -y

# --- Helper function to draw Rectangles using Midpoint Line ---
def draw_box(x, y, w, h):
    draw_line(x, y, x + w, y)
    draw_line(x + w, y, x + w, y + h)
    draw_line(x + w, y + h, x, y + h)
    draw_line(x, y + h, x, y)

# --- Sami's Logic: Collision and Generation ---
def update_game_objects():
    global score, lives, game_over, player_x, obstacles, life_tokens

    if game_over: return

    # Move obstacles and check collisions
    for obs in obstacles[:]:
        obs[1] -= player_speed # Move down
        
        # Collision Detection (Feature 2)
        if (player_x < obs[0] + 40 and player_x + 40 > obs[0] and
            player_y < obs[1] + 40 and player_y + 40 > obs[1]):
            lives -= 1
            obstacles.remove(obs)
            if lives <= 0: game_over = True
            
        elif obs[1] < 0:
            obstacles.remove(obs)
            score += 10

    # Life Token Logic (Feature 3)
    for token in life_tokens[:]:
        token[1] -= player_speed
        if (player_x < token[0] + 20 and player_x + 40 > token[0] and
            player_y < token[1] + 20 and player_y + 40 > token[1]):
            lives += 1
            life_tokens.remove(token)
        elif token[1] < 0:
            life_tokens.remove(token)

    # Spawning (Feature 1)
    if random.random() < 0.02: # Obstacle rate
        obstacles.append([random.randint(50, 400), W_HEIGHT])
    if random.random() < 0.005: # Life token rate
        life_tokens.append([random.randint(50, 400), W_HEIGHT])

# --- Display & Inputs ---
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glPointSize(2)

    # Draw Player (Naimur's Part)
    glColor3f(0.0, 1.0, 1.0) # Cyan
    draw_box(player_x, player_y, player_width, 60)

    # Draw Obstacles (Sami's Part 1)
    glColor3f(1.0, 0.0, 0.0) # Red
    for obs in obstacles:
        draw_box(obs[0], obs[1], 40, 40)

    # Draw Life Tokens (Sami's Part 3)
    glColor3f(0.0, 1.0, 0.0) # Green
    for token in life_tokens:
        draw_box(token[0], token[1], 20, 20)

    update_game_objects()
    glutSwapBuffers()

def keyboard_listener(key, x, y):
    global player_x
    if key == b'a': player_x -= 20
    if key == b'd': player_x += 20
    glutPostRedisplay()

def idle():
    # Since glutTimerFunc is banned, we use idle for movement
    time.sleep(0.01)
    glutPostRedisplay()

# --- Initialization ---
glutInit()
glutInitWindowSize(W_WIDTH, W_HEIGHT)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutCreateWindow(b"Skateboard Endless Runner")
glOrtho(0, W_WIDTH, 0, W_HEIGHT, -1, 1)
glutDisplayFunc(display)
glutKeyboardFunc(keyboard_listener)
glutIdleFunc(idle)
glutMainLoop()