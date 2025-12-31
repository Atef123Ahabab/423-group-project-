from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
STANDALONE_MODE = False
W_Width, W_Height = 800, 600
score = 0
distance_score = 0
level = 1
level_threshold = 300
difficulty_multiplier = 1.0
zone_distance = 0
zone_length = 500
zone_collision_occurred = False
game_state = "playing"
paused = False
player_x = 0
player_y = -200
player_lives = 5
player_invincible_timer = 0
distance_traveled = 0
current_multiplier = 1
base_speed = 2.0
current_speed = base_speed
obstacle_spawn_chance = 0.02
obstacles = []
collectibles = []
background_lines = []
animation_frame = 0
def find_zone(x1, y1, x2, y2):
    zone = 0
    if x1 >= 0 and y1 >= 0 and x2 >= 0 and y2 >= 0:
        zone = 0
    elif x1 <= 0 and y1 >= 0 and x2 <= 0 and y2 >= 0:
        zone = 1
    elif x1 <= 0 and y1 <= 0 and x2 <= 0 and y2 <= 0:
        zone = 2
    elif x1 >= 0 and y1 <= 0 and x2 >= 0 and y2 <= 0:
        zone = 3
    return zone
def convert_coordinate(x, y):
    global W_Width, W_Height
    a = x - (W_Width / 2)
    b = (W_Height / 2) - y
    return a, b
def draw_points(x, y, size=2):
    glPointSize(size)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()
def draw_line(x1, y1, x2, y2):
    zone = find_zone(x1, y1, x2, y2)
    if zone == 0:
        draw_line_zone0(x1, y1, x2, y2)
    elif zone == 1:
        draw_line_zone0(y1, x1, y2, x2)
    elif zone == 2:
        draw_line_zone0(-y1, x1, -y2, x2)
    elif zone == 3:
        draw_line_zone0(-x1, y1, -x2, y2)
def draw_line_zone0(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    incrE = 2 * dy
    incrNE = 2 * (dy - dx)
    y = y1
    for x in range(int(x1), int(x2) + 1):
        draw_points(x, y)
        if d > 0:
            d += incrNE
            y += 1
        else:
            d += incrE
def draw_circle(cx, cy, radius):
    x = 0
    y = radius
    d = 1 - radius
    while x <= y:
        draw_points(cx + x, cy + y)
        draw_points(cx - x, cy + y)
        draw_points(cx + x, cy - y)
        draw_points(cx - x, cy - y)
        draw_points(cx + y, cy + x)
        draw_points(cx - y, cy + x)
        draw_points(cx + y, cy - x)
        draw_points(cx - y, cy - x)
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1
def draw_filled_circle(cx, cy, radius):
    for r in range(radius, 0, -2):
        draw_circle(cx, cy, r)
def draw_rect(x, y, width, height):
    draw_line(x, y, x + width, y)
    draw_line(x + width, y, x + width, y + height)
    draw_line(x + width, y + height, x, y + height)
    draw_line(x, y + height, x, y)
def draw_filled_rect(x, y, width, height):
    for i in range(int(height)):
        draw_line(x, y + i, x + width, y + i)
def draw_skateboard_character(x, y):
    glColor3f(1.0, 0.8, 0.6)
    draw_filled_circle(int(x), int(y + 40), 15)
    glColor3f(0.2, 0.4, 0.8)
    draw_filled_rect(int(x - 12), int(y + 10), 24, 30)
    draw_line(x - 12, y + 35, x - 25, y + 20)
    draw_line(x + 12, y + 35, x + 25, y + 20)
    glColor3f(0.1, 0.1, 0.1)
    draw_line(x - 5, y + 10, x - 10, y - 15)
    draw_line(x + 5, y + 10, x + 10, y - 15)
    glColor3f(0.9, 0.1, 0.1)
    draw_filled_rect(int(x - 20), int(y - 20), 40, 5)
    glColor3f(0.2, 0.2, 0.2)
    draw_filled_circle(int(x - 12), int(y - 22), 3)
    draw_filled_circle(int(x + 12), int(y - 22), 3)
def draw_obstacle(x, y, obs_type):
    if obs_type == "box":
        glColor3f(0.6, 0.3, 0.0)
        draw_filled_rect(int(x - 20), int(y), 40, 40)
        glColor3f(0.4, 0.2, 0.0)
        draw_rect(x - 20, y, 40, 40)
    elif obs_type == "cone":
        glColor3f(1.0, 0.5, 0.0)
        draw_line(x, y + 40, x - 15, y)
        draw_line(x, y + 40, x + 15, y)
        draw_line(x - 15, y, x + 15, y)
    elif obs_type == "barrier":
        glColor3f(0.9, 0.9, 0.1)
        draw_filled_rect(int(x - 25), int(y), 50, 20)
        glColor3f(0.0, 0.0, 0.0)
        for i in range(0, 50, 10):
            draw_line(x - 25 + i, y, x - 25 + i, y + 20)
def draw_life_token(x, y):
    glColor3f(1.0, 0.0, 0.0)
    draw_filled_circle(int(x - 8), int(y + 10), 8)
    draw_filled_circle(int(x + 8), int(y + 10), 8)
    draw_line(x - 15, y + 10, x, y - 10)
    draw_line(x + 15, y + 10, x, y - 10)
    for i in range(-15, 15):
        ratio = abs(i) / 15.0
        y_pos = y + 10 - int(20 * ratio)
        draw_line(x + i, y + 10, x + i, y_pos)
def draw_road():
    glColor3f(0.3, 0.3, 0.3)
    draw_filled_rect(-150, -300, 300, 600)
    glColor3f(1.0, 1.0, 1.0)
    for line in background_lines:
        draw_filled_rect(-2, int(line), 4, 40)
        draw_filled_rect(48, int(line), 4, 40)
def draw_zone_indicator():
    zone_progress = (zone_distance % zone_length) / zone_length
    zone_num = int(zone_distance / zone_length) % 3
    is_bonus_zone = (zone_num == 1)
    if is_bonus_zone:
        glColor3f(1.0, 0.84, 0.0)
    else:
        glColor3f(0.5, 0.5, 0.5)
    bar_width = int(zone_progress * 200)
    draw_filled_rect(250, 250, bar_width, 20)
    glColor3f(1.0, 1.0, 1.0)
    draw_rect(250, 250, 200, 20)
def draw_hud():
    glColor3f(1.0, 1.0, 1.0)
    draw_text(-380, 270, f"Score: {int(score)}")
    draw_text(-380, 250, f"Level: {level}")
    draw_text(-380, 230, f"Lives: {player_lives}")
    zone_num = int(zone_distance / zone_length) % 3
    multiplier = 2 if zone_num == 1 else 1
    if multiplier > 1:
        glColor3f(1.0, 0.84, 0.0)
        draw_text(250, 230, f"x{multiplier} BONUS ZONE!")
    glColor3f(1.0, 1.0, 1.0)
    draw_text(250, 210, "Zone Progress")
def draw_text(x, y, text):
    try:
        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))
    except:
        pass
def draw_game_over():
    glColor3f(1.0, 0.0, 0.0)
    draw_text(-100, 50, "GAME OVER!")
    glColor3f(1.0, 1.0, 1.0)
    draw_text(-120, 0, f"Final Score: {int(score)}")
    draw_text(-120, -30, f"Level Reached: {level}")
    draw_text(-150, -80, "Press 'R' to Restart")
    draw_text(-150, -110, "Press 'ESC' to Quit")
def update_score(player_speed=None, game_state_param="playing"):
    global score, distance_score, distance_traveled, zone_distance, zone_collision_occurred
    speed = player_speed if player_speed is not None else current_speed
    if game_state_param == "playing":
        distance_increment = speed * 0.1
        distance_score += distance_increment
        distance_traveled += distance_increment
        zone_distance += distance_increment
        zone_num = int(zone_distance / zone_length) % 3
        multiplier = 2 if zone_num == 1 else 1
        score = int(distance_score * multiplier) if zone_num == 1 else int(distance_score)
        if zone_distance >= zone_length:
            zone_distance = 0
            zone_collision_occurred = False
def update_level_progression(update_difficulty_callback=None):
    global level, score, level_threshold
    new_level = (score // level_threshold) + 1
    if new_level > level:
        level = new_level
        print(f"=" * 50)
        print(f"LEVEL UP! Now at Level {level}")
        print(f"Next level at score {level * level_threshold}")
        print(f"=" * 50)
        if update_difficulty_callback:
            update_difficulty_callback()
        else:
            update_difficulty()
def update_level():
    global level
    new_level = int(score / level_threshold) + 1
    if new_level > level:
        level = new_level
        update_difficulty()
def update_difficulty():
    global difficulty_multiplier, level, current_speed, obstacle_spawn_chance
    difficulty_multiplier = 1.0 + (level - 1) * 0.3
    current_speed = base_speed + (level - 1) * 0.3
    obstacle_spawn_chance = 0.02 + (level - 1) * 0.005
    obstacle_spawn_chance = min(obstacle_spawn_chance, 0.05)
    print(f"Difficulty increased to {difficulty_multiplier:.1f}x")
def get_obstacle_spawn_rate_from_difficulty():
    global level
    spawn_rate = max(30, 60 - level * 5)
    return spawn_rate
def get_score():
    return score
def get_level():
    return level
def get_difficulty_multiplier():
    return difficulty_multiplier
def get_zone_multiplier():
    zone_num = int(zone_distance / zone_length) % 3
    return 2 if zone_num == 1 else 1
def get_zone_progress():
    return (zone_distance % zone_length) / zone_length
def reset_scoring():
    global score, distance_score, level, difficulty_multiplier
    global zone_distance, zone_collision_occurred, distance_traveled
    score = 0
    distance_score = 0
    distance_traveled = 0
    level = 1
    difficulty_multiplier = 1.0
    zone_distance = 0
    zone_collision_occurred = False
    print("Scoring system reset!")
def draw_score_hud(x, y):
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(x, y)
    text = f"Score: {score}"
    for char in text:
        try:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        except:
            pass
def draw_level_hud(x, y):
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(x, y)
    text = f"Level: {level}"
    for char in text:
        try:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        except:
            pass
def draw_game_over_stats(center_x, center_y):
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(center_x - 80, center_y - 50)
    text = f"Final Score: {score}"
    for char in text:
        try:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        except:
            pass
    glRasterPos2f(center_x - 70, center_y - 80)
    text = f"Level Reached: {level}"
    for char in text:
        try:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        except:
            pass
def spawn_obstacle():
    if random.random() < obstacle_spawn_chance:
        lane = random.choice([-1, 0, 1])
        obs_type = random.choice(["box", "cone", "barrier"])
        obstacles.append({
            "x": lane * 50,
            "y": 350,
            "type": obs_type
        })
def spawn_collectible():
    if random.random() < 0.005:
        lane = random.choice([-1, 0, 1])
        collectibles.append({
            "x": lane * 50,
            "y": 350
        })
def update_obstacles():
    global obstacles
    for obs in obstacles:
        obs["y"] -= current_speed
    obstacles = [obs for obs in obstacles if obs["y"] > -350]
def update_collectibles():
    global collectibles
    for col in collectibles:
        col["y"] -= current_speed
    collectibles = [col for col in collectibles if col["y"] > -350]
def update_background():
    global background_lines
    for i in range(len(background_lines)):
        background_lines[i] -= current_speed
    background_lines = [line for line in background_lines if line > -350]
    while len(background_lines) < 10:
        if background_lines:
            background_lines.append(background_lines[-1] + 80)
        else:
            background_lines.append(300)
def check_collision():
    global player_lives, game_state, player_invincible_timer, zone_collision_occurred
    if player_invincible_timer > 0:
        return
    player_pos_x = player_x * 50
    for obs in obstacles:
        if abs(player_pos_x - obs["x"]) < 35 and abs(player_y - obs["y"]) < 40:
            player_lives -= 1
            player_invincible_timer = 60
            zone_collision_occurred = True
            if player_lives <= 0:
                game_state = "game_over"
            obstacles.remove(obs)
            break
def check_collectible():
    global player_lives, collectibles
    player_pos_x = player_x * 50
    for col in collectibles:
        if abs(player_pos_x - col["x"]) < 30 and abs(player_y - col["y"]) < 30:
            player_lives = min(player_lives + 1, 5)
            collectibles.remove(col)
            break
def reset_game():
    global game_state, player_x, player_lives, score, level, distance_traveled
    global zone_distance, current_speed, obstacles, collectibles, background_lines
    global zone_collision_occurred, player_invincible_timer, distance_score
    global difficulty_multiplier
    game_state = "playing"
    player_x = 0
    player_lives = 5
    score = 0
    distance_score = 0
    distance_traveled = 0
    level = 1
    zone_distance = 0
    difficulty_multiplier = 1.0
    current_speed = base_speed
    obstacles = []
    collectibles = []
    background_lines = [i * 80 - 300 for i in range(10)]
    zone_collision_occurred = False
    player_invincible_timer = 0
    print("Game reset!")
def animate():
    global animation_frame, player_invincible_timer
    if game_state == "playing" and not paused:
        animation_frame += 1
        if player_invincible_timer > 0:
            player_invincible_timer -= 1
        update_score()
        update_level()
        update_difficulty()
        update_obstacles()
        update_collectibles()
        update_background()
        spawn_obstacle()
        spawn_collectible()
        check_collision()
        check_collectible()
    glutPostRedisplay()
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    if game_state == "playing":
        draw_road()
        for obs in obstacles:
            draw_obstacle(obs["x"], obs["y"], obs["type"])
        for col in collectibles:
            draw_life_token(col["x"], col["y"])
        if player_invincible_timer == 0 or animation_frame % 10 < 5:
            draw_skateboard_character(player_x * 50, player_y)
        draw_zone_indicator()
        draw_hud()
        if paused:
            glColor3f(1.0, 1.0, 0.0)
            draw_text(-50, 0, "PAUSED")
    elif game_state == "game_over":
        draw_game_over()
    glutSwapBuffers()
def keyboard(key, x, y):
    global player_x, paused, game_state
    if game_state == "playing":
        if key == b'a' or key == b'A':
            player_x = max(player_x - 1, -1)
        elif key == b'd' or key == b'D':
            player_x = min(player_x + 1, 1)
        elif key == b'p' or key == b'P':
            paused = not paused
    if key == b'r' or key == b'R':
        reset_game()
    if key == b'\x1b':
        glutLeaveMainLoop()
def special_input(key, x, y):
    global player_x
    if game_state == "playing":
        if key == GLUT_KEY_LEFT:
            player_x = max(player_x - 1, -1)
        elif key == GLUT_KEY_RIGHT:
            player_x = min(player_x + 1, 1)
def init():
    glClearColor(0.1, 0.1, 0.2, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-W_Width/2, W_Width/2, -W_Height/2, W_Height/2)
    reset_game()
def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(W_Width, W_Height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Skateboard Endless Runner - Tithi's Scoring System")
    init()
    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_input)
    print("=" * 70)
    print("TITHI'S SCORING & GAME FLOW MODULE")
    print("=" * 70)
    print("\nFEATURES IMPLEMENTED:")
    print("1. Distance-Based Score Increment")
    print("2. Level Progression System (every 300 points)")
    print("3. Score-Based Difficulty Feedback")
    print("4. Zone Multiplier System (BONUS: 2x score zones)")
    print("\nCONTROLS:")
    print("  A/D or Arrow Keys - Move Left/Right")
    print("  P - Pause")
    print("  R - Restart")
    print("  ESC - Quit")
    print("\nGAME INFO:")
    print("  - Avoid obstacles (boxes, cones, barriers)")
    print("  - Collect hearts for extra lives")
    print("  - Watch for BONUS ZONES (2x score!)")
    print("  - Difficulty increases with each level")
    print("\nGood luck!")
    print("=" * 70)
    glutMainLoop()
if __name__ == "__main__":
    STANDALONE_MODE = True
    main()
else:
    print("[Tithi Module] Scoring & Level System loaded")
    print("  Available functions:")
    print("  - update_score(speed, state)")
    print("  - update_level_progression(callback)")
    print("  - update_difficulty()")
    print("  - get_score(), get_level(), get_difficulty_multiplier()")
    print("  - reset_scoring()")
    print("  - draw_score_hud(x, y), draw_level_hud(x, y)")