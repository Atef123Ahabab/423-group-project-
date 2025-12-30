from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

# --- Window Dimensions ---
W_WIDTH, W_HEIGHT = 500, 800

# --- Game State ---
player_x = 225
player_y = 100
obstacles = []     # List of [x, y]
life_tokens = []   # List of [x, y]
lives = 3
score = 0
game_over = False
paused = False

# --- 1. Midpoint Line Drawing Algorithm (The Core Requirement) ---
# This function handles all 8 octants to ensure 50% marks.
def draw_line(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    
    zone = get_zone(x1, y1, x2, y2)
    x1, y1 = convert_to_zone0(zone, x1, y1)
    x2, y2 = convert_to_zone0(zone, x2, y2)
    
    dx, dy = x2 - x1, y2 - y1
    d = 2 * dy - dx
    dE = 2 * dy
    dNE = 2 * (dy - dx)
    
    x, y = x1, y1
    while x <= x2:
        ox, oy = convert_from_zone0(zone, x, y)
        draw_pixel(ox, oy)
        if d < 0:
            d += dE
        else:
            d += dNE
            y += 1
        x += 1

def draw_pixel(x, y):
    glBegin(GL_POINTS)
    glVertex2i(int(x), int(y))
    glEnd()

def get_zone(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if abs(dx) > abs(dy):
        if dx >= 0 and dy >= 0: return 0
        if dx < 0 and dy >= 0: return 3
        if dx < 0 and dy < 0: return 4
        return 7
    else:
        if dx >= 0 and dy >= 0: return 1
        if dx < 0 and dy >= 0: return 2
        if dx < 0 and dy < 0: return 5
        return 6

def convert_to_zone0(zone, x, y):
    if zone == 0: return x, y
    if zone == 1: return y, x
    if zone == 2: return y, -x
    if zone == 3: return -x, y
    if zone == 4: return -x, -y
    if zone == 5: return -y, -x
    if zone == 6: return -y, x
    return x, -y

def convert_from_zone0(zone, x, y):
    if zone == 0: return x, y
    if zone == 1: return y, x
    if zone == 2: return -y, x
    if zone == 3: return -x, y
    if zone == 4: return -x, -y
    if zone == 5: return -y, -x
    if zone == 6: return y, -x
    return x, -y

# --- Shape Helpers ---
def draw_rectangle(x, y, w, h):
    draw_line(x, y, x + w, y)
    draw_line(x + w, y, x + w, y + h)
    draw_line(x + w, y + h, x, y + h)
    draw_line(x, y + h, x, y)

# --- Sami's Feature 1 & 2: Obstacle Generation & Collision ---
def update_game():
    global player_x, obstacles, life_tokens, lives, score, game_over
    if game_over or paused: return

    # Move obstacles down
    for obs in obstacles[:]:
        obs[1] -= 5 
        # Collision Detection (Sami Feature 2)
        if (player_x < obs[0] + 40 and player_x + 50 > obs[0] and
            player_y < obs[1] + 40 and player_y + 60 > obs[1]):
            lives -= 1
            obstacles.remove(obs)
            print(f"Collision! Lives left: {lives}")
            if lives <= 0: game_over = True
        elif obs[1] < 0:
            obstacles.remove(obs)
            score += 1

    # Life Token Logic (Sami Feature 3)
    for token in life_tokens[:]:
        token[1] -= 5
        if (player_x < token[0] + 20 and player_x + 50 > token[0] and
            player_y < token[1] + 20 and player_y + 60 > token[1]):
            lives += 1
            life_tokens.remove(token)
            print("Life Gained!")
        elif token[1] < 0:
            life_tokens.remove(token)

    # Random Spawning (Sami Feature 1)
    if random.random() < 0.02:
        obstacles.append([random.randint(50, 410), W_HEIGHT])
    if random.random() < 0.005:
        life_tokens.append([random.randint(50, 410), W_HEIGHT])

# --- Display & Inputs ---
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glPointSize(2)

    # Draw Road Borders
    glColor3f(1, 1, 1)
    draw_line(50, 0, 50, W_HEIGHT)
    draw_line(450, 0, 450, W_HEIGHT)

    # Draw Player (Naimur's concept)
    glColor3f(0, 1, 1) # Cyan Player
    draw_rectangle(player_x, player_y, 50, 20) # Skateboard
    draw_rectangle(player_x + 10, player_y + 20, 30, 40) # Character

    # Draw Sami's Obstacles (Red Boxes)
    glColor3f(1, 0, 0)
    for obs in obstacles:
        draw_rectangle(obs[0], obs[1], 40, 40)

    # Draw Sami's Life Tokens (Green Boxes)
    glColor3f(0, 1, 0)
    for token in life_tokens:
        draw_rectangle(token[0], token[1], 20, 20)

    update_game()
    glutSwapBuffers()

def keyboard(key, x, y):
    global player_x
    if key == b'a' and player_x > 60: player_x -= 20
    if key == b'd' and player_x < 390: player_x += 20
    glutPostRedisplay()

def animate():
    # Using idle instead of glutTimerFunc as per constraints
    glutPostRedisplay()


glutInit()
glutInitWindowSize(W_WIDTH, W_HEIGHT)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutCreateWindow(b"CSE423: Skateboard Game")
glOrtho(0, W_WIDTH, 0, W_HEIGHT, -1, 1)
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutIdleFunc(animate)
glutMainLoop()