from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
W_WIDTH, W_HEIGHT = 500, 800
player_x = 225
player_y = 100
obstacles = []
life_tokens = []
lives = 3
max_lives = 5
score = 0
game_over = False
paused = False
obstacle_spawn_timer = 0
obstacle_spawn_rate = 60
token_spawn_rate = 200
obstacle_types = ["box", "barrier", "cone"]
lanes = [450, 550, 650, 750]
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
def draw_rectangle(x, y, w, h):
    draw_line(x, y, x + w, y)
    draw_line(x + w, y, x + w, y + h)
    draw_line(x + w, y + h, x, y + h)
    draw_line(x, y + h, x, y)
def draw_filled_rect(x, y, w, h):
    for i in range(int(h)):
        draw_line(int(x), int(y + i), int(x + w), int(y + i))
def draw_circle_midpoint(cx, cy, radius):
    x = 0
    y = radius
    d = 1 - radius
    while x <= y:
        draw_pixel(cx + x, cy + y)
        draw_pixel(cx - x, cy + y)
        draw_pixel(cx + x, cy - y)
        draw_pixel(cx - x, cy - y)
        draw_pixel(cx + y, cy + x)
        draw_pixel(cx - y, cy + x)
        draw_pixel(cx + y, cy - x)
        draw_pixel(cx - y, cy - x)
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1
def draw_filled_circle(cx, cy, radius):
    for r in range(radius, 0, -2):
        draw_circle_midpoint(cx, cy, r)
def spawn_obstacle():
    global obstacles, obstacle_types, lanes
    obs_type = random.choice(obstacle_types)
    lane = random.randint(0, 3)
    x = lanes[lane]
    y = W_HEIGHT + 50
    obstacle = {
        "type": obs_type,
        "x": x,
        "y": y,
        "width": 40,
        "height": 40 if obs_type != "barrier" else 20,
        "lane": lane
    }
    obstacles.append(obstacle)
    print(f"Spawned {obs_type} obstacle in lane {lane}")
def update_obstacles(speed=5):
    global obstacles, score
    for obs in obstacles[:]:
        obs["y"] -= speed
        if obs["y"] < -100:
            obstacles.remove(obs)
            score += 1
def draw_obstacles():
    for obs in obstacles:
        if obs["type"] == "box":
            glColor3f(0.6, 0.3, 0.0)
            draw_filled_rect(
                obs["x"] - obs["width"]/2,
                obs["y"],
                obs["width"],
                obs["height"]
            )
            glColor3f(0.4, 0.2, 0.0)
            draw_rectangle(
                obs["x"] - obs["width"]/2,
                obs["y"],
                obs["width"],
                obs["height"]
            )
        elif obs["type"] == "barrier":
            glColor3f(0.9, 0.9, 0.1)
            draw_filled_rect(
                obs["x"] - obs["width"]/2,
                obs["y"],
                obs["width"],
                obs["height"]
            )
            glColor3f(0.0, 0.0, 0.0)
            for i in range(0, int(obs["width"]), 10):
                draw_line(
                    obs["x"] - obs["width"]/2 + i, obs["y"],
                    obs["x"] - obs["width"]/2 + i, obs["y"] + obs["height"]
                )
        elif obs["type"] == "cone":
            glColor3f(1.0, 0.5, 0.0)
            for i in range(int(obs["height"])):
                ratio = i / obs["height"]
                width = obs["width"] * (1 - ratio)
                draw_line(
                    int(obs["x"] - width/2), int(obs["y"] + i),
                    int(obs["x"] + width/2), int(obs["y"] + i)
                )
            glColor3f(1.0, 1.0, 1.0)
            stripe_y = obs["y"] + obs["height"] * 0.6
            stripe_width = obs["width"] * 0.5
            for i in range(5):
                draw_line(
                    int(obs["x"] - stripe_width/2), int(stripe_y + i),
                    int(obs["x"] + stripe_width/2), int(stripe_y + i)
                )
def spawn_life_token():
    global life_tokens, lanes
    lane = random.randint(0, 3)
    x = lanes[lane]
    y = W_HEIGHT + 50
    token = {
        "x": x,
        "y": y,
        "size": 20,
        "lane": lane,
        "animation": 0
    }
    life_tokens.append(token)
    print(f"Spawned life token in lane {lane}")
def update_life_tokens(speed=5):
    global life_tokens
    for token in life_tokens[:]:
        token["y"] -= speed
        token["animation"] += 0.1
        if token["y"] < -50:
            life_tokens.remove(token)
def draw_life_tokens():
    for token in life_tokens:
        pulse = 1.0 + math.sin(token["animation"]) * 0.2
        size = token["size"] * pulse
        glColor3f(1.0, 0.0, 0.0)
        draw_filled_circle(int(token["x"] - size/4), int(token["y"] + size/2), int(size/3))
        draw_filled_circle(int(token["x"] + size/4), int(token["y"] + size/2), int(size/3))
        for i in range(int(size/2)):
            ratio = i / (size/2)
            width = size * (1 - ratio)
            draw_line(
                int(token["x"] - width/2), int(token["y"] + size/4 - i),
                int(token["x"] + width/2), int(token["y"] + size/4 - i)
            )
        glColor3f(1.0, 1.0, 1.0)
        draw_filled_circle(int(token["x"]), int(token["y"]), int(size * 0.2))
def check_collision_rect(obj1_x, obj1_y, obj1_w, obj1_h, obj2_x, obj2_y, obj2_w, obj2_h):
    return (obj1_x < obj2_x + obj2_w and
            obj1_x + obj1_w > obj2_x and
            obj1_y < obj2_y + obj2_h and
            obj1_y + obj1_h > obj2_y)
def handle_obstacle_collisions(player_x, player_y, player_width=50, player_height=60):
    global obstacles, lives, game_over
    collision_occurred = False
    for obs in obstacles[:]:
        if check_collision_rect(
            player_x - player_width/2, player_y,
            player_width, player_height,
            obs["x"] - obs["width"]/2, obs["y"],
            obs["width"], obs["height"]
        ):
            obstacles.remove(obs)
            lives -= 1
            collision_occurred = True
            print(f"Collision! Lives remaining: {lives}")
            if lives <= 0:
                game_over = True
                print("Game Over! No lives remaining!")
    return collision_occurred
def handle_token_collection(player_x, player_y, player_width=50, player_height=60):
    global life_tokens, lives
    token_collected = False
    for token in life_tokens[:]:
        if check_collision_rect(
            player_x - player_width/2, player_y,
            player_width, player_height,
            token["x"] - token["size"]/2, token["y"],
            token["size"], token["size"]
        ):
            life_tokens.remove(token)
            if lives < max_lives:
                lives += 1
                token_collected = True
                print(f"Life token collected! Lives: {lives}")
    return token_collected
def update_game():
    global player_x, obstacles, life_tokens, lives, score, game_over, paused
    global obstacle_spawn_timer
    if game_over or paused:
        return
    update_obstacles(5)
    update_life_tokens(5)
    handle_obstacle_collisions(player_x, player_y)
    handle_token_collection(player_x, player_y)
    obstacle_spawn_timer += 1
    if obstacle_spawn_timer >= obstacle_spawn_rate:
        spawn_obstacle()
        obstacle_spawn_timer = 0
    if random.random() < 0.005:
        spawn_life_token()
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glPointSize(2)
    glColor3f(1, 1, 1)
    draw_line(50, 0, 50, W_HEIGHT)
    draw_line(450, 0, 450, W_HEIGHT)
    glColor3f(0, 1, 1)
    draw_rectangle(player_x - 25, player_y, 50, 20)
    draw_rectangle(player_x - 15, player_y + 20, 30, 40)
    draw_obstacles()
    draw_life_tokens()
    glColor3f(1, 1, 1)
    draw_text(10, W_HEIGHT - 30, f"Lives: {lives} | Score: {score}")
    if game_over:
        glColor3f(1, 0, 0)
        draw_text(W_WIDTH/2 - 50, W_HEIGHT/2, "GAME OVER!")
    update_game()
    glutSwapBuffers()
def draw_text(x, y, text):
    try:
        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))
    except:
        pass
def keyboard(key, x, y):
    global player_x, game_over, paused
    if key == b'a' and player_x > 100:
        player_x -= 125
    elif key == b'd' and player_x < 350:
        player_x += 125
    elif key == b'p':
        paused = not paused
    elif key == b'r':
        reset_game()
    glutPostRedisplay()
def animate():
    if not game_over and not paused:
        glutPostRedisplay()
def get_lives():
    return lives
def set_lives(new_lives):
    global lives
    lives = new_lives
def get_obstacles():
    return obstacles
def get_life_tokens():
    return life_tokens
def set_obstacle_spawn_rate(rate):
    global obstacle_spawn_rate
    obstacle_spawn_rate = rate
def reset_game():
    global obstacles, life_tokens, lives, score, game_over, paused, obstacle_spawn_timer
    obstacles.clear()
    life_tokens.clear()
    lives = 3
    score = 0
    game_over = False
    paused = False
    obstacle_spawn_timer = 0
    print("Game reset!")
def reset_obstacles():
    global obstacles, life_tokens, obstacle_spawn_timer
    obstacles.clear()
    life_tokens.clear()
    obstacle_spawn_timer = 0
    print("Obstacles and life tokens reset!")
def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(W_WIDTH, W_HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Sami's Features - Obstacles & Collision Demo")
    glClearColor(0.1, 0.1, 0.2, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, W_WIDTH, 0, W_HEIGHT)
    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutKeyboardFunc(keyboard)
    print("=" * 60)
    print("SAMI'S FEATURES DEMO - Obstacles & Collision Handling")
    print("=" * 60)
    print("\nFEATURES:")
    print("1. Obstacle Generation (boxes, barriers, cones)")
    print("2. Collision Detection System")
    print("3. Life Tokens (Health Pickups)")
    print("\nCONTROLS:")
    print("  A - Move Left")
    print("  D - Move Right")
    print("  P - Pause")
    print("  R - Reset")
    print("\nGOAL: Dodge obstacles and collect hearts!")
    print("=" * 60)
    glutMainLoop()
if __name__ == "__main__":
    main()
