from OpenGL.GL import *
from OpenGL.GLUT import *
import random
import math
game_state = "playing"
game_time = 0
camera_shake = 0
camera_zoom = 1.0
camera_y_offset = 0
camera_transition = 0.0
camera_mode = "third_person"
camera_perspective_fov = 60
use_perspective = False
background_offset = 0
weather_effect = "clear"
time_of_day = "day"
bg_layers = [
    {"offset": 0, "speed": 0.2, "color": (0.3, 0.5, 0.7)},
    {"offset": 0, "speed": 0.5, "color": (0.4, 0.6, 0.8)},
    {"offset": 0, "speed": 0.8, "color": (0.5, 0.5, 0.5)},
]
def draw_filled_rect(x, y, w, h):
    glBegin(GL_TRIANGLES)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x, y + h)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()
def draw_line(x0, y0, x1, y1):
    dx = abs(int(x1) - int(x0))
    dy = abs(int(y1) - int(y0))
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    xi, yi = int(x0), int(y0)
    glBegin(GL_POINTS)
    while True:
        glVertex2i(xi, yi)
        if xi == int(x1) and yi == int(y1):
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            xi += sx
        if e2 < dx:
            err += dx
            yi += sy
    glEnd()
def trigger_camera_shake(intensity):
    global camera_shake
    camera_shake = intensity
def apply_camera_shake():
    global camera_shake
    if camera_shake > 0:
        shake_x = random.randint(-5, 5) * (camera_shake / 10.0)
        shake_y = random.randint(-5, 5) * (camera_shake / 10.0)
        glTranslatef(shake_x, shake_y, 0)
        camera_shake -= 1
def apply_camera_zoom(score):
    global camera_zoom
    if score > 500:
        camera_zoom = 0.95
def setup_camera_view(player_x, player_y, player_speed):
    global camera_mode, camera_y_offset, camera_transition, camera_zoom
    W_Width, W_Height = 1200, 800
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    zoom_factor = camera_zoom
    if camera_mode == "first_person":
        camera_transition = min(camera_transition + 0.05, 1.0)
        target_y_offset = -200 * camera_transition
        camera_y_offset += (target_y_offset - camera_y_offset) * 0.1
        zoom_factor = 1.1 + (0.2 * camera_transition)
        glOrtho(-W_Width * 0.1 * zoom_factor, 
                W_Width * (1 + 0.1 * zoom_factor), 
                camera_y_offset * zoom_factor, 
                W_Height + camera_y_offset * zoom_factor, 
                -1, 1)
    else:
        camera_transition = max(camera_transition - 0.05, 0.0)
        target_y_offset = 0
        camera_y_offset += (target_y_offset - camera_y_offset) * 0.1
        zoom_factor = 1.0
        glOrtho(0, W_Width, 0, W_Height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
def toggle_camera_mode():
    global camera_mode
    if camera_mode == "third_person":
        camera_mode = "first_person"
        print("\n" + "="*50)
        print(">>> FIRST PERSON VIEW ACTIVATED <<<")
        print("Camera follows player closely")
        print("="*50)
    else:
        camera_mode = "third_person"
        print("\n" + "="*50)
        print(">>> THIRD PERSON VIEW ACTIVATED <<<")
        print("Standard bird's eye view")
        print("="*50)
def update_background(player_speed):
    global bg_layers, background_offset
    background_offset += player_speed
    for layer in bg_layers:
        layer["offset"] += player_speed * layer["speed"]
        if layer["offset"] > 800:
            layer["offset"] = 0
def draw_background():
    global time_of_day, bg_layers
    W_Width, W_Height = 1200, 800
    if time_of_day == "day":
        sky_color = (0.5, 0.7, 1.0)
    else:
        sky_color = (0.1, 0.1, 0.3)
    glColor3f(*sky_color)
    draw_filled_rect(0, 0, W_Width, W_Height)
    for i, layer in enumerate(bg_layers):
        building_height = 150 + i * 50
        building_width = 80 - i * 10
        spacing = 150
        if time_of_day == "day":
            color = (0.3 + i * 0.1, 0.3 + i * 0.1, 0.3 + i * 0.1)
        else:
            color = (0.05 + i * 0.05, 0.05 + i * 0.05, 0.1 + i * 0.05)
        glColor3f(*color)
        offset = layer["offset"]
        y = -offset
        while y < W_Height + building_height:
            draw_filled_rect(20 + i * 10, y, building_width, building_height)
            draw_filled_rect(W_Width - building_width - 20 - i * 10, y, building_width, building_height)
            if time_of_day == "day":
                glColor3f(0.7, 0.9, 1.0)
                for wx in range(2):
                    for wy in range(3):
                        window_x = 30 + i * 10 + wx * 25
                        window_y = y + 20 + wy * 40
                        draw_filled_rect(window_x, window_y, 15, 20)
                        window_x = W_Width - building_width + 10 - i * 10 + wx * 25
                        draw_filled_rect(window_x, window_y, 15, 20)
                glColor3f(*color)
            y += spacing + building_height
def draw_road():
    global background_offset
    W_Width, W_Height = 1200, 800
    glColor3f(0.3, 0.3, 0.35)
    draw_filled_rect(50, 0, 350, W_Height)
    glColor3f(1.0, 1.0, 0.0)
    lane_offset = int(background_offset) % 80
    for y in range(-lane_offset, W_Height, 80):
        draw_filled_rect(140, y, 8, 40)
        draw_filled_rect(260, y, 8, 40)
    glColor3f(1.0, 1.0, 1.0)
    draw_filled_rect(48, 0, 4, W_Height)
    draw_filled_rect(398, 0, 4, W_Height)
def draw_weather_effects():
    global weather_effect, background_offset
    W_Width, W_Height = 1200, 800
    if weather_effect == "rain":
        glColor3f(0.6, 0.7, 0.9)
        for i in range(50):
            x = random.randint(0, W_Width)
            y = (random.randint(0, W_Height) + int(background_offset * 5)) % W_Height
            draw_line(x, y, x + 2, y - 20)
    elif weather_effect == "fog":
        glColor4f(0.7, 0.7, 0.7, 0.3)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        draw_filled_rect(0, 0, W_Width, W_Height)
        glDisable(GL_BLEND)
def update_environment_based_on_score(score):
    global weather_effect, time_of_day
    if score > 500 and score < 1000:
        weather_effect = "rain"
    elif score > 1000:
        weather_effect = "fog"
    else:
        weather_effect = "clear"
    if score > 400:
        time_of_day = "night"
    else:
        time_of_day = "day"
def scale_difficulty_with_score(score, level, set_spawn_rate_callback):
    obstacle_spawn_rate = max(30, 60 - level * 5)
    set_spawn_rate_callback(obstacle_spawn_rate)
    return obstacle_spawn_rate
def reset_game_state(reset_player_callback, reset_obstacles_callback, reset_scoring_callback):
    global game_state, game_time, camera_shake, camera_zoom
    global background_offset, weather_effect, time_of_day, bg_layers
    game_state = "playing"
    game_time = 0
    camera_shake = 0
    camera_zoom = 1.0
    background_offset = 0
    weather_effect = "clear"
    camera_y_offset = 0
    camera_transition = 0.0
    time_of_day = "day"
    for layer in bg_layers:
        layer["offset"] = 0
    reset_player_callback()
    reset_obstacles_callback()
    reset_scoring_callback()
    print("=" * 60)
    print("GAME RESET - All systems reinitialized!")
    print("=" * 60)
def get_game_state():
    return game_state
def set_game_state(state):
    global game_state
    game_state = state
def toggle_pause():
    global game_state
    if game_state == "playing":
        game_state = "paused"
    elif game_state == "paused":
        game_state = "playing"
def increment_game_time():
    global game_time
    game_time += 1
def get_background_offset():
    return background_offset
def get_camera_mode():
    return camera_mode
def get_camera_y_offset():
    return camera_y_offset