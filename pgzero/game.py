import pgzrun
import requests
import time
import os

WIDTH = 640
HEIGHT = 480
TILE_SIZE = 32
SERVER_URL = 'http://127.0.0.1:5000'

class Cat:
    def __init__(self, player_id, name, x, y):
        self.player_id = player_id
        self.name = name
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * TILE_SIZE
        self.pixel_y = y * TILE_SIZE
        self.target_x = self.pixel_x
        self.target_y = self.pixel_y
        self.direction = 'down'
        self.action = 'wait'
        self.frame = 0
        self.frame_delay = 0.15
        self.last_frame_time = time.time()
        self.images = self.load_images()

    def load_images(self):
        actions = ['walk', 'wait']
        directions = ['up', 'down', 'left', 'right']
        images_dict = {}
        for action in actions:
            for direction in directions:
                key = f"{action}_{direction}"
                folder = os.path.join("images", key)
                frames = []
                i = 0
                while True:
                    path = os.path.join(folder, f"{i}.png")
                    if not os.path.exists(path):
                        break
                    frames.append(images.load(os.path.join(key, f"{i}.png")))
                    i += 1
                images_dict[key] = frames
        return images_dict

    def update_position(self, new_x, new_y):
        dx = new_x - self.grid_x
        dy = new_y - self.grid_y

        if dx == 1:
            self.direction = 'right'
        elif dx == -1:
            self.direction = 'left'
        elif dy == 1:
            self.direction = 'down'
        elif dy == -1:
            self.direction = 'up'

        if dx != 0 or dy != 0:
            self.action = 'walk'
            self.target_x = new_x * TILE_SIZE
            self.target_y = new_y * TILE_SIZE
            self.grid_x = new_x
            self.grid_y = new_y
        else:
            self.action = 'wait'

    def animate(self):
        now = time.time()
        if now - self.last_frame_time > self.frame_delay:
            self.frame = (self.frame + 1) % len(self.images[f"{self.action}_{self.direction}"])
            self.last_frame_time = now

    def draw(self):
        key = f"{self.action}_{self.direction}"
        frame_list = self.images.get(key, [])
        if frame_list:
            image = frame_list[self.frame % len(frame_list)]
            screen.blit(image, (self.pixel_x, self.pixel_y))
        screen.draw.text(self.name, (self.pixel_x, self.pixel_y - 10), color='white', fontsize=16)

    def update_pixel_position(self):
        speed = 2
        if self.pixel_x < self.target_x:
            self.pixel_x += speed
        elif self.pixel_x > self.target_x:
            self.pixel_x -= speed

        if self.pixel_y < self.target_y:
            self.pixel_y += speed
        elif self.pixel_y > self.target_y:
            self.pixel_y -= speed


class Coin:
    def __init__(self, x, y):
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * TILE_SIZE
        self.pixel_y = y * TILE_SIZE
        self.image = "coin"

    def draw(self):
        screen.blit(self.image, (self.pixel_x, self.pixel_y))


cats = {}
coin = None


def fetch_game_state():
    global coin
    try:
        res = requests.get(f"{SERVER_URL}/game_state")
        data = res.json()
        for player in data['players']:
            pid = player['id']
            if pid not in cats:
                cats[pid] = Cat(pid, player['name'], player['x'], player['y'])
            else:
                cats[pid].update_position(player['x'], player['y'])

        c = data['coin']
        coin = Coin(c['x'], c['y'])
    except Exception as e:
        print("Error fetching game state:", e)


def update():
    fetch_game_state()
    for cat in cats.values():
        cat.animate()
        cat.update_pixel_position()


def draw():
    screen.clear()
    if coin:
        coin.draw()
    for cat in cats.values():
        cat.draw()


pgzrun.go()
