from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

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

player_x_2d = 550.0
player_y_2d = 150.0
player_base_y = 150.0
ground_y = 150.0
player_lane = 1
lanes_2d = [450, 550, 650, 750]
window_width = 1200
window_height = 800
player_velocity_y = 0
player_is_jumping = False
player_is_sliding = False
player_speed = 2.0
base_speed = 2.0
max_speed = 15.0
acceleration = 0.02
speed_increment = 0.02
deceleration = 0.5
slide_duration = 0
slide_duration_frames = 30
current_lane = 1
gravity_2d = -1.2
jump_strength_2d = 18
animation_frame = 0
player_width = 30
player_height = 40

obstacles = []
life_tokens = []
lives = 3
max_lives = 5
obstacle_spawn_rate = 60
obstacle_types = ["box", "barrier", "cone"]
lanes = [450, 550, 650, 750]

score = 0
distance_score = 0
level = 1
level_threshold = 300
difficulty_multiplier = 1.0
zone_distance = 0
zone_length = 500
zone_collision_occurred = False

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

def draw_circle_2d(cx, cy, radius, filled=True):
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

def draw_triangle(x1, y1, x2, y2, x3, y3):
    glBegin(GL_TRIANGLES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glVertex2f(x3, y3)
    glEnd()

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

def draw_skateboard_character_2d():
    global player_x_2d, player_y_2d, animation_frame
    global player_is_sliding, player_speed
    px = player_x_2d
    py = player_y_2d
    if player_is_sliding:
        py -= 15
        glColor3f(0.9, 0.5, 0.2)
        draw_filled_rect(px - 15, py - 5, 30, 8)
        glColor3f(0.2, 0.2, 0.2)
        draw_circle_2d(px - 10, py - 5, 4)
        draw_circle_2d(px + 10, py - 5, 4)
        glColor3f(0.2, 0.6, 0.9)
        draw_filled_rect(px - 10, py + 3, 20, 15)
        glColor3f(1.0, 0.8, 0.6)
        draw_circle_2d(px, py + 25, 8)
        glColor3f(1.0, 0.8, 0.6)
        draw_filled_rect(px - 5, py + 10, 15, 5)
        return
    glColor3f(0.9, 0.5, 0.2)
    draw_filled_rect(px - 15, py - 5, 30, 8)
    glColor3f(0.2, 0.2, 0.2)
    draw_circle_2d(px - 10, py - 5, 4)
    draw_circle_2d(px + 10, py - 5, 4)
    glColor3f(0.3, 0.3, 0.8)
    leg_offset = math.sin(animation_frame * 0.2) * 3
    draw_filled_rect(px - 10, py + 3, 6, int(15 + leg_offset))
    draw_filled_rect(px + 4, py + 3, 6, int(15 - leg_offset))
    glColor3f(0.2, 0.6, 0.9)
    draw_filled_rect(px - 10, py + 18, 20, 18)
    glColor3f(1.0, 0.8, 0.6)
    draw_circle_2d(px, py + 45, 8)
    glColor3f(0.9, 0.1, 0.1)
    draw_circle_2d(px, py + 48, 9)
    draw_filled_rect(px - 9, py + 45, 18, 5)
    glColor3f(1.0, 0.8, 0.6)
    arm_offset = math.sin(animation_frame * 0.2) * 2
    draw_filled_rect(px - 15, int(py + 25 + arm_offset), 5, 12)
    draw_filled_rect(px + 10, int(py + 25 - arm_offset), 5, 12)

def draw_skateboard_character():
    draw_skateboard_character_2d()

def update_player_movement():
    global player_x_2d, player_y_2d, player_velocity_y, player_is_jumping
    global player_is_sliding, slide_duration, animation_frame, player_speed
    if player_speed < max_speed:
        player_speed += speed_increment
    animation_frame += player_speed * 0.1
    if player_is_jumping:
        player_velocity_y += gravity_2d
        player_y_2d += player_velocity_y
        if player_y_2d <= ground_y:
            player_y_2d = ground_y
            player_velocity_y = 0
            player_is_jumping = False
    else:
        player_y_2d = ground_y
        player_velocity_y = 0
    if player_is_sliding:
        slide_duration -= 1
        if slide_duration <= 0:
            player_is_sliding = False
            slide_duration = 0

def move_left():
    global current_lane, player_x_2d
    if current_lane > 0:
        current_lane -= 1
        player_x_2d = lanes_2d[current_lane]

def move_right():
    global current_lane, player_x_2d
    if current_lane < len(lanes_2d) - 1:
        current_lane += 1
        player_x_2d = lanes_2d[current_lane]

def jump():
    global player_is_jumping, player_velocity_y
    if not player_is_jumping:
        player_is_jumping = True
        player_velocity_y = jump_strength_2d

def slide():
    global player_is_sliding, slide_duration
    if not player_is_jumping and not player_is_sliding:
        player_is_sliding = True
        slide_duration = slide_duration_frames

def get_player_position():
    return (player_x_2d, player_y_2d)

def get_player_lane():
    return current_lane

def get_player_speed():
    return player_speed

def set_player_speed(new_speed):
    global player_speed
    player_speed = max(base_speed, min(new_speed, max_speed))

def handle_collision():
    global player_speed
    player_speed = max(base_speed, player_speed - deceleration)

def reset_player():
    global current_lane, player_x_2d, player_y_2d, player_velocity_y
    global player_is_jumping, player_is_sliding, player_speed, animation_frame
    current_lane = 1
    player_x_2d = lanes_2d[current_lane]
    player_y_2d = ground_y
    player_velocity_y = 0
    player_is_jumping = False
    player_is_sliding = False
    player_speed = base_speed
    animation_frame = 0

def get_character_width():
    return 30 if not player_is_sliding else 35

def get_character_height():
    return 55 if not player_is_sliding else 25

def draw_filled_circle(cx, cy, radius):
    for r in range(radius, 0, -2):
        x = 0
        y = r
        d = 1 - r
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
    global obstacles
    for obs in obstacles[:]:
        obs["y"] -= speed
        if obs["y"] < -100:
            obstacles.remove(obs)

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
            for i in range(int(obs["width"])):
                draw_line(obs["x"] - obs["width"]/2 + i, obs["y"], 
                         obs["x"] - obs["width"]/2 + i, obs["y"] + obs["height"])
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
    global obstacles, lives
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

def get_lives():
    return lives

def set_obstacle_spawn_rate(rate):
    global obstacle_spawn_rate
    obstacle_spawn_rate = rate

def reset_obstacles():
    global obstacles, life_tokens
    obstacles.clear()
    life_tokens.clear()

def update_score(player_speed_param=None, game_state_param="playing"):
    global score, distance_score, zone_distance, zone_collision_occurred
    speed = player_speed_param if player_speed_param is not None else player_speed
    if game_state_param == "playing":
        distance_increment = speed * 0.1
        distance_score += distance_increment
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

def update_difficulty():
    global difficulty_multiplier, level
    difficulty_multiplier = 1.0 + (level - 1) * 0.3
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

def reset_scoring():
    global score, distance_score, level, difficulty_multiplier
    global zone_distance, zone_collision_occurred
    score = 0
    distance_score = 0
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

def setup_camera_view(player_x, player_y, player_speed_cam):
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

def update_background(player_speed_bg):
    global bg_layers, background_offset
    background_offset += player_speed_bg
    for layer in bg_layers:
        layer["offset"] += player_speed_bg * layer["speed"]
        if layer["offset"] > 800:
            layer["offset"] = 0

def update_environment_based_on_score(score_env):
    global weather_effect, day_night_cycle
    if score_env < 300:
        day_night_cycle = "day"
        weather_effect = "clear"
    elif score_env >= 300 and score_env < 800:
        day_night_cycle = "dusk"
        weather_effect = "dust"
    elif score_env >= 800 and score_env < 1500:
        day_night_cycle = "night"
        weather_effect = "volcano"
    else:
        day_night_cycle = "night"
        weather_effect = "volcano"

def scale_difficulty_with_score(score_diff, level_diff):
    obstacle_spawn_rate_diff = max(30, 60 - level_diff * 5)
    set_obstacle_spawn_rate(obstacle_spawn_rate_diff)
    return obstacle_spawn_rate_diff

def reset_game_state():
    global game_state, game_time, camera_shake, camera_zoom
    global background_offset, weather_effect, bg_layers, day_night_cycle, lives
    game_state = "playing"
    game_time = 0
    camera_shake = 0
    camera_zoom = 1.0
    background_offset = 0
    weather_effect = "clear"
    day_night_cycle = "day"
    lives = 3
    for layer in bg_layers:
        layer["offset"] = 0
    reset_player()
    reset_obstacles()
    reset_scoring()
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
    draw_score_hud(500, 750)
    draw_level_hud(500, 720)
    glColor3f(1.0, 1.0, 1.0)
    player_speed_hud = get_player_speed()
    draw_text(500, 690, f"Speed: {player_speed_hud:.1f}")
    lives_hud = get_lives()
    for i in range(lives_hud):
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
    multiplier = get_zone_multiplier()
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
    draw_game_over_stats(420, 400)
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
    player_x_disp, player_y_disp = get_player_position()
    player_speed_disp = get_player_speed()
    setup_camera_view(player_x_disp, player_y_disp, player_speed_disp)
    apply_camera_shake()
    draw_prehistoric_background()
    draw_prehistoric_road()
    draw_obstacles()
    draw_life_tokens()
    draw_skateboard_character()
    draw_weather_effects()
    draw_hud()
    if game_state == "game_over":
        draw_game_over()
    elif game_state == "paused":
        draw_pause_screen()
    glutSwapBuffers()

def update():
    global game_state, game_time, camera_zoom
    if game_state == "playing":
        game_time += 1
        player_speed_upd = get_player_speed()
        score_upd = get_score()
        level_upd = get_level()
        update_background(player_speed_upd)
        update_player_movement()
        update_obstacles(player_speed_upd)
        update_life_tokens(player_speed_upd)
        player_x_upd, player_y_upd = get_player_position()
        player_width_upd = get_character_width()
        player_height_upd = get_character_height()
        collision = handle_obstacle_collisions(player_x_upd, player_y_upd, player_width_upd, player_height_upd)
        if collision:
            trigger_camera_shake(10)
            handle_collision()
            if get_lives() <= 0:
                game_state = "game_over"
        token_collected = handle_token_collection(player_x_upd, player_y_upd, player_width_upd, player_height_upd)
        if token_collected:
            trigger_camera_shake(3)
            trigger_camera_zoom(1.15, 20)
        update_score(player_speed_upd, game_state)
        update_level_progression(update_difficulty)
        update_environment_based_on_score(score_upd)
        scale_difficulty_with_score(score_upd, level_upd)
        if camera_zoom > 1.0:
            camera_zoom = max(1.0, camera_zoom - 0.01)
        elif camera_zoom < 1.0:
            camera_zoom = min(1.0, camera_zoom + 0.01)
        if game_time % get_obstacle_spawn_rate_from_difficulty() == 0:
            spawn_obstacle()
        if random.randint(0, 300) == 0:
            spawn_life_token()
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
        jump()
    if key == b's' or key == b'S':
        slide()
    if key == b'a' or key == b'A':
        move_left()
    if key == b'd' or key == b'D':
        move_right()
    if key == b'c' or key == b'C' or key == b'v' or key == b'V':
        toggle_camera_mode()

def special_keyboard_handler(key, x, y):
    if game_state != "playing":
        return
    if key == GLUT_KEY_LEFT:
        move_left()
    elif key == GLUT_KEY_RIGHT:
        move_right()
    elif key == GLUT_KEY_DOWN:
        slide()
    elif key == GLUT_KEY_UP:
        jump()

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
    print("\n✓ ALL 4 MODULES MERGED INTO ONE FILE")
    print("✓ No external dependencies required\n")
    print("Starting game...\n")
    glutMainLoop()

if __name__ == "__main__":
    main()
