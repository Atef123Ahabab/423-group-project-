from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import naimur
import sami
import tithi
import Atef
W_WIDTH, W_HEIGHT = 1200, 800
game_state = "playing"
game_time = 0
camera_shake = 0
camera_zoom = 1.0
camera_y_offset = 0
camera_transition = 0.0
camera_mode = "third_person"
background_offset = 0
weather_effect = "clear"
time_period = "prehistoric"
day_night_cycle = "day"
bg_layers = [
    {"offset": 0, "speed": 0.15, "type": "mountains_far"},
    {"offset": 0, "speed": 0.35, "type": "volcano"},
    {"offset": 0, "speed": 0.6, "type": "mountains_near"},
]
dinosaurs = []
pterodactyls = []
volcano_particles = []
def draw_filled_rect(x, y, w, h):
    glBegin(GL_TRIANGLES)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x, y + h)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()
def draw_circle(cx, cy, radius):
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
    glBegin(GL_TRIANGLES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glVertex2f(x3, y3)
    glEnd()
def draw_prehistoric_background():
    global bg_layers, background_offset, day_night_cycle
    if day_night_cycle == "day":
        glColor3f(0.8, 0.5, 0.3)
    elif day_night_cycle == "dusk":
        glColor3f(0.6, 0.3, 0.2)
    else:
        glColor3f(0.15, 0.1, 0.2)
    draw_filled_rect(0, 0, W_WIDTH, W_HEIGHT)
    if day_night_cycle == "day":
        glColor3f(0.95, 0.8, 0.5)
    elif day_night_cycle == "dusk":
        glColor3f(0.9, 0.5, 0.2)
    else:
        glColor3f(0.7, 0.7, 0.8)
    draw_circle(1000, 650, 60)
    layer = bg_layers[0]
    glColor3f(0.3, 0.25, 0.2)
    y_offset = -layer["offset"] % 800
    for i in range(3):
        base_y = i * 300 - y_offset
        for j in range(5):
            x = j * 250 + 50
            draw_triangle(x, base_y, x + 100, base_y + 200, x + 200, base_y)
    layer = bg_layers[1]
    glColor3f(0.4, 0.3, 0.25)
    y_offset = -layer["offset"] % 800
    volcano_x = W_WIDTH - 300
    volcano_y = 100 - (y_offset % 200)
    draw_triangle(volcano_x - 100, volcano_y, volcano_x, volcano_y + 250, volcano_x + 100, volcano_y)
    glColor3f(0.9, 0.3, 0.1)
    draw_triangle(volcano_x - 30, volcano_y + 250, volcano_x, volcano_y + 280, volcano_x + 30, volcano_y + 250)
    glColor3f(0.5, 0.5, 0.5)
    smoke_offset = int(background_offset * 0.3)
    for i in range(3):
        smoke_y = volcano_y + 280 + i * 40 + (smoke_offset % 50)
        if smoke_y < W_HEIGHT:
            draw_circle(volcano_x + random.randint(-20, 20), smoke_y, 30 - i * 5)
    layer = bg_layers[2]
    glColor3f(0.5, 0.4, 0.3)
    y_offset = -layer["offset"] % 800
    for i in range(2):
        base_y = i * 400 - y_offset
        for j in range(4):
            x = j * 300
            draw_triangle(x, base_y, x + 120, base_y + 150, x + 240, base_y)
    glColor3f(0.2, 0.15, 0.1)
    ptero_offset = int(background_offset * 0.5) % W_WIDTH
    for i in range(2):
        x = (ptero_offset + i * 500) % W_WIDTH
        y = 500 + i * 100
        draw_triangle(x, y, x + 30, y + 10, x + 20, y - 10)
        draw_triangle(x - 20, y + 5, x, y, x + 10, y + 15)
        draw_triangle(x + 20, y + 5, x + 50, y + 15, x + 30, y)
def draw_prehistoric_road():
    global background_offset
    glColor3f(0.4, 0.35, 0.25)
    draw_filled_rect(400, 0, 400, W_HEIGHT)
    glColor3f(0.35, 0.3, 0.2)
    rock_offset = int(background_offset) % 100
    for y in range(-rock_offset, W_HEIGHT, 100):
        for x in [420, 500, 580, 660, 740, 780]:
            if random.randint(0, 2) == 0:
                draw_circle(x + random.randint(-10, 10), y + random.randint(0, 50), random.randint(5, 12))
    glColor3f(0.6, 0.5, 0.4)
    lane_offset = int(background_offset) % 80
    for y in range(-lane_offset, W_HEIGHT, 80):
        draw_filled_rect(495, y, 10, 30)
        draw_filled_rect(595, y, 10, 30)
        draw_filled_rect(695, y, 10, 30)
    glColor3f(0.5, 0.45, 0.35)
    draw_filled_rect(395, 0, 10, W_HEIGHT)
    draw_filled_rect(795, 0, 10, W_HEIGHT)
    glColor3f(0.9, 0.85, 0.8)
    bone_offset = int(background_offset * 0.7) % 150
    for y in range(-bone_offset, W_HEIGHT, 150):
        draw_filled_rect(350, y, 20, 8)
        draw_circle(348, y + 4, 6)
        draw_circle(372, y + 4, 6)
        draw_filled_rect(820, y + 50, 20, 8)
        draw_circle(818, y + 54, 6)
        draw_circle(842, y + 54, 6)
def draw_weather_effects():
    global weather_effect, background_offset
    if weather_effect == "dust":
        glColor3f(0.7, 0.6, 0.5)
        for i in range(40):
            x = (random.randint(0, W_WIDTH) + int(background_offset * 2)) % W_WIDTH
            y = random.randint(0, W_HEIGHT)
            draw_circle(x, y, 3)
    elif weather_effect == "volcano":
        glColor3f(0.3, 0.3, 0.3)
        for i in range(30):
            x = random.randint(0, W_WIDTH)
            y = (random.randint(0, W_HEIGHT) + int(background_offset * 3)) % W_HEIGHT
            draw_circle(x, y, 4)
def trigger_camera_shake(intensity):
    global camera_shake
    camera_shake = intensity

def trigger_camera_zoom(zoom_level, duration=30):
    global camera_zoom
    camera_zoom = zoom_level
def apply_camera_shake():
    global camera_shake
    if camera_shake > 0:
        shake_x = random.randint(-5, 5) * (camera_shake / 10.0)
        shake_y = random.randint(-5, 5) * (camera_shake / 10.0)
        glTranslatef(shake_x, shake_y, 0)
        camera_shake -= 1
def setup_camera_view(player_x, player_y, player_speed):
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
    global camera_mode
    if camera_mode == "third_person":
        camera_mode = "first_person"
        print("\n>>> FIRST PERSON VIEW ACTIVATED <<<")
    else:
        camera_mode = "third_person"
        print("\n>>> THIRD PERSON VIEW ACTIVATED <<<")
def update_background(player_speed):
    global bg_layers, background_offset
    background_offset += player_speed
    for layer in bg_layers:
        layer["offset"] += player_speed * layer["speed"]
        if layer["offset"] > 800:
            layer["offset"] = 0
def update_environment_based_on_score(score):
    global weather_effect, day_night_cycle
    if score < 300:
        day_night_cycle = "day"
        weather_effect = "clear"
    elif score >= 300 and score < 800:
        day_night_cycle = "dusk"
        weather_effect = "dust"
    elif score >= 800 and score < 1500:
        day_night_cycle = "night"
        weather_effect = "volcano"
    else:
        day_night_cycle = "night"
        weather_effect = "volcano"
def scale_difficulty_with_score(score, level):
    obstacle_spawn_rate = max(30, 60 - level * 5)
    sami.set_obstacle_spawn_rate(obstacle_spawn_rate)
    return obstacle_spawn_rate
def reset_game_state():
    global game_state, game_time, camera_shake, camera_zoom
    global background_offset, weather_effect, bg_layers, day_night_cycle
    game_state = "playing"
    game_time = 0
    camera_shake = 0
    camera_zoom = 1.0
    background_offset = 0
    weather_effect = "clear"
    day_night_cycle = "day"
    for layer in bg_layers:
        layer["offset"] = 0
    naimur.reset_player()
    sami.reset_game()
    tithi.reset_scoring()
    print("=" * 60)
    print("GAME RESET - All systems reinitialized!")
    print("=" * 60)
def draw_text(x, y, text):
    try:
        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    except:
        pass
def draw_hud():
    tithi.draw_score_hud(500, 750)
    tithi.draw_level_hud(500, 720)
    glColor3f(1.0, 1.0, 1.0)
    player_speed = naimur.get_player_speed()
    draw_text(500, 690, f"Speed: {player_speed:.1f}")
    lives = sami.get_lives()
    for i in range(lives):
        x = 500 + i * 30
        y = 650
        glColor3f(1.0, 0.2, 0.2)
        draw_circle(x - 3, y + 5, 5)
        draw_circle(x + 3, y + 5, 5)
        draw_triangle(x, y - 5, x - 7, y + 3, x + 7, y + 3)
    glColor3f(0.9, 0.9, 0.7)
    draw_text(20, 750, "PREHISTORIC RUNNER")
    draw_text(20, 720, "Arrows: Move")
    draw_text(20, 690, "Space: Jump")
    draw_text(20, 660, "Down: Slide")
    draw_text(20, 630, "P: Pause | R: Restart")
    draw_text(20, 600, "C/V: Camera")
    if camera_mode == "first_person":
        glColor3f(0.0, 1.0, 0.0)
        draw_text(20, 560, "VIEW: 1st Person")
    else:
        glColor3f(0.5, 0.5, 1.0)
        draw_text(20, 560, "VIEW: 3rd Person")
    multiplier = tithi.get_zone_multiplier()
    if multiplier > 1:
        glColor3f(1.0, 0.84, 0.0)
        draw_text(500, 620, f"x{multiplier} BONUS ZONE!")
def draw_game_over():
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
    glColor4f(0.0, 0.0, 0.0, 0.5)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    draw_filled_rect(0, 0, W_WIDTH, W_HEIGHT)
    glDisable(GL_BLEND)
    glColor3f(1.0, 1.0, 0.0)
    draw_text(520, 400, "PAUSED")
    glColor3f(1.0, 1.0, 1.0)
    draw_text(470, 370, "Press P to Resume")
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    player_x, player_y = naimur.get_player_position()
    player_speed = naimur.get_player_speed()
    setup_camera_view(player_x, player_y, player_speed)
    apply_camera_shake()
    draw_prehistoric_background()
    draw_prehistoric_road()
    sami.draw_obstacles()
    sami.draw_life_tokens()
    naimur.draw_skateboard_character()
    draw_weather_effects()
    draw_hud()
    if game_state == "game_over":
        draw_game_over()
    elif game_state == "paused":
        draw_pause_screen()
    glutSwapBuffers()
def update():
    global game_state, game_time
    if game_state == "playing":
        game_time += 1
        player_speed = naimur.get_player_speed()
        score = tithi.get_score()
        level = tithi.get_level()
        update_background(player_speed)
        naimur.update_player_movement()
        sami.update_obstacles(player_speed)
        sami.update_life_tokens(player_speed)
        player_x, player_y = naimur.get_player_position()
        player_width = naimur.get_character_width()
        player_height = naimur.get_character_height()
        collision = sami.handle_obstacle_collisions(player_x, player_y, player_width, player_height)
        if collision:
            trigger_camera_shake(10)
            naimur.handle_collision()
            if sami.get_lives() <= 0:
                game_state = "game_over"
        token_collected = sami.handle_token_collection(player_x, player_y, player_width, player_height)
        if token_collected:
            trigger_camera_shake(3)
            trigger_camera_zoom(1.15, 20)
        tithi.update_score(player_speed, game_state)
        tithi.update_level_progression(tithi.update_difficulty)
        update_environment_based_on_score(score)
        scale_difficulty_with_score(score, level)
        global camera_zoom
        if camera_zoom > 1.0:
            camera_zoom = max(1.0, camera_zoom - 0.01)
        elif camera_zoom < 1.0:
            camera_zoom = min(1.0, camera_zoom + 0.01)
        if game_time % tithi.get_obstacle_spawn_rate_from_difficulty() == 0:
            sami.spawn_obstacle()
        if random.randint(0, 300) == 0:
            sami.spawn_life_token()
    glutPostRedisplay()
def keyboard_handler(key, x, y):
    global game_state
    if key == b'r' or key == b'R':
        reset_game_state()
        return
    if key == b'\x1b':
        import sys
        sys.exit()
    if key == b'p' or key == b'P':
        if game_state == "playing":
            game_state = "paused"
        elif game_state == "paused":
            game_state = "playing"
        return
    if game_state != "playing":
        return
    if key == b' ' or key == b'w' or key == b'W':
        naimur.jump()
    if key == b's' or key == b'S':
        naimur.slide()
    if key == b'a' or key == b'A':
        naimur.move_left()
    if key == b'd' or key == b'D':
        naimur.move_right()
    if key == b'c' or key == b'C' or key == b'v' or key == b'V':
        toggle_camera_mode()
def special_keyboard_handler(key, x, y):
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
def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, W_WIDTH, 0, W_HEIGHT, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPointSize(2)
def main():
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
