import tkinter as tk
import time
import random
import winsound
from enum import Enum

ANIMATION_FILES = {
    "idle_right": "idle_right.gif",
    "idle_left": "idle_left.gif",
    "standing_up_idle_right": "standing_up_idle_right.gif",
    "standing_up_idle_left": "standing_up_idle_left.gif",
    "standing_up_idle_1_right": "standing_up_idle_1_right.gif",
    "standing_up_idle_1_left": "standing_up_idle_1_left.gif",
    "sit_down_right": "sit_down_right.gif",
    "sit_down_left": "sit_down_left.gif",
    "napping": "napping.gif",
    "looking_around_napping": "looking_around_while_napping.gif",
    "stand_up_right": "stand_up_right.gif",
    "stand_up_left": "stand_up_left.gif",
    "run_right": "running_right.gif",
    "run_left": "running_left.gif",
    "fast_run_right": "fast_running_right.gif",
    "fast_run_left": "fast_running_left.gif",
    "walk_2_right": "walking_on_2_legs_right.gif",
    "walk_2_left": "walking_on_2_legs_left.gif",
    "stop_right": "running_stop_right.gif",
    "stop_left": "running_stop_left.gif",
    "angry_right": "angry_right.gif",
    "angry_left": "angry_left.gif",
}


class Direction(Enum):
    LEFT = -1
    RIGHT = 1


class PetState(Enum):
    IDLE = "idle"
    RUN = "run"
    FAST_RUN = "fast_run"
    WALK = "walk_2"
    STOP = "stop"
    SIT_DOWN = "sit_down"
    STAND_UP = "stand_up"
    STANDING_IDLE = "standing_up_idle"
    STANDING_IDLE_1 = "standing_up_idle_1"
    NAP = "napping"
    LOOK_NAP = "looking_around_napping"
    ANGRY = "angry"


class MovementController:
    SPEED_MAP = {PetState.FAST_RUN: 6, PetState.RUN: 3, PetState.WALK: 1}

    def get_speed(self, state):
        return self.SPEED_MAP.get(state, 0)


class Pet:
    def __init__(self):
        self.window = tk.Tk()

        # CONFIG
        self.scale = 3
        self.frame_delay = 100  # ms per frame

        self.movement = MovementController()

        self.anims = self.load_all_animations()

        self.direction = Direction.RIGHT  # 1:right, -1:left
        self.vertical_dir = 0  # vertical movement disabled for horizontal-only

        self.state = PetState.IDLE
        self.frames = self.anims[self.get_anim_key()]
        self.frame_idx = 0

        self.start_time = time.time()
        self.duration = 5

        self.x = 500
        self.y = 500

        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.config(bg="black")
        self.window.wm_attributes("-transparentcolor", "black")

        self.label = tk.Label(self.window, bg="black", bd=0)
        self.label.pack()

        self.screen_w = self.window.winfo_screenwidth()
        self.screen_h = self.window.winfo_screenheight()

        self.last_update_time = time.time()

        # Drag & drop variables
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # Click tracking for drag vs click distinction
        self.click_start_x = 0
        self.click_start_y = 0

        # Angry state timing
        self.angry_until = 0

        # Bind left button events for drag and click distinction
        self.label.bind("<ButtonPress-1>", self.start_drag_or_click)
        self.label.bind("<B1-Motion>", self.do_drag)
        self.label.bind("<ButtonRelease-1>", self.stop_drag_or_click)

        # Bind right-click to make angry
        self.label.bind("<Button-3>", self.make_angry)

        # Sound timing
        self.last_sound_time = time.time()
        self.sound_interval = random.randint(600, 1200)  # 14–17 minutes (in seconds)

        self.update()
        self.window.mainloop()

    def load_all_animations(self):
        anims = {}

        for name, filename in ANIMATION_FILES.items():
            path = f"assets/gifs/{filename}"
            anims[name] = self.load_gif(path)

        return anims

    def play_meow(self):
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)  # stop previous sound
            winsound.PlaySound(
                "assets/sounds/meow.wav", winsound.SND_FILENAME | winsound.SND_ASYNC
            )
        except Exception as e:
            print("Sound error:", e)

    def load_gif(self, path):
        frames = []
        idx = 0
        while True:
            try:
                frame = tk.PhotoImage(file=path, format=f"gif -index {idx}")
                frames.append(frame.zoom(self.scale, self.scale))
                idx += 1
            except tk.TclError:
                break
        if not frames:
            print(f"Missing file: {path}")
        return frames

    def get_anim_key(self):
        if self.state in [PetState.NAP, PetState.LOOK_NAP]:
            return self.state.value

        direction = "right" if self.direction == Direction.RIGHT else "left"
        return f"{self.state.value}_{direction}"

    def set_state(self, state, duration=0):
        self.state = state
        key = self.get_anim_key()

        self.frames = self.anims.get(key, [])
        self.frame_idx = 0
        self.start_time = time.time()
        self.duration = duration

    # Left click press - record starting position, reset dragging flag
    def start_drag_or_click(self, event):
        self.dragging = False
        self.click_start_x = event.x
        self.click_start_y = event.y
        self.drag_offset_x = event.x
        self.drag_offset_y = event.y

    # Left click drag - if moved enough, consider dragging and move window
    def do_drag(self, event):
        dx = abs(event.x - self.click_start_x)
        dy = abs(event.y - self.click_start_y)
        if dx > 5 or dy > 5:
            self.dragging = True
            new_x = self.window.winfo_pointerx() - self.drag_offset_x
            new_y = self.window.winfo_pointery() - self.drag_offset_y
            self.x = new_x
            self.y = new_y
            self.window.geometry(f"+{int(self.x)}+{int(self.y)}")

    # Left click release - if dragged, just stop dragging; if not dragged, do nothing (no angry)
    def stop_drag_or_click(self, event):
        if self.dragging:
            self.dragging = False
            self.start_time = time.time()
        else:
            # No angry on left-click without drag
            pass

    # Right click makes pet angry
    def make_angry(self, event=None):
        self.set_state(PetState.ANGRY, 3)
        self.angry_until = time.time() + self.duration

    def transition(self):
        if time.time() < self.angry_until:
            return

        curr = self.state

        # SIT / STAND / STOP -> IDLE
        if curr in [PetState.SIT_DOWN, PetState.STAND_UP, PetState.STOP]:
            self.set_state(PetState.IDLE, random.randint(4, 8))

        # NAPPING
        elif curr == PetState.NAP:
            if random.random() < 0.2:
                self.set_state(PetState.STAND_UP, 0)
            else:
                if random.random() < 0.4:
                    self.set_state(PetState.LOOK_NAP, 8)
                else:
                    self.set_state(PetState.NAP, 8)

        # IDLE -> movement or sit
        elif curr == PetState.IDLE:
            rand = random.random()

            if rand < 0.5:

                if random.random() < 0.3:
                    self.direction = (
                        Direction.LEFT
                        if self.direction == Direction.RIGHT
                        else Direction.RIGHT
                    )

                self.set_state(
                    random.choice([PetState.RUN, PetState.WALK, PetState.FAST_RUN]),
                    random.randint(5, 10),
                )

            elif rand < 0.7:

                if random.random() < 0.7:
                    self.set_state(PetState.SIT_DOWN, 0)
                else:
                    self.set_state(PetState.NAP, 10)

            else:
                self.set_state(PetState.STANDING_IDLE_1, 5)

        # MOVING STATES
        elif curr in [PetState.RUN, PetState.WALK, PetState.FAST_RUN]:

            if random.random() < 0.4:
                self.set_state(PetState.STOP, 0)
            else:
                self.duration = random.randint(3, 6)

        else:
            self.set_state(PetState.IDLE, 5)

    def handle_sound(self, now):
        if now - self.last_sound_time > self.sound_interval:
            self.play_meow()
            self.last_sound_time = now
            self.sound_interval = random.randint(600, 1200)

    def update_animation(self):
        if self.frames:
            self.label.config(image=self.frames[self.frame_idx])
            self.frame_idx = (self.frame_idx + 1) % len(self.frames)

    def move_pet(self):
        speed = self.movement.get_speed(self.state)
        self.x += speed * self.direction.value

    def handle_wall_collision(self):
        if not self.frames:
            return

        pet_w = self.frames[0].width()

        hit_wall = False

        if self.x < 0:
            self.x = 5
            self.direction = Direction.RIGHT
            hit_wall = True

        elif self.x > self.screen_w - pet_w:
            self.x = self.screen_w - pet_w - 5
            self.direction = Direction.LEFT
            hit_wall = True

        if hit_wall:
            self.set_state(PetState.STOP, 0)

    def update(self):
        now = time.time()

        self.handle_sound(now)

        if self.dragging:
            self.update_animation()
            self.window.geometry(f"+{int(self.x)}+{int(self.y)}")
            self.window.after(self.frame_delay, self.update)
            return

        if now < self.angry_until:
            if self.state != PetState.ANGRY:
                self.set_state(PetState.ANGRY, 3)

            self.update_animation()
            self.window.geometry(f"+{int(self.x)}+{int(self.y)}")
            self.window.after(self.frame_delay, self.update)
            return

        self.move_pet()

        self.handle_wall_collision()

        self.update_animation()

        self.window.geometry(f"+{int(self.x)}+{int(self.y)}")

        time_passed = now - self.start_time
        if now >= self.angry_until:
            if (self.duration == 0 and self.frame_idx == 0) or (
                self.duration > 0 and time_passed > self.duration
            ):
                self.transition()

        self.window.after(self.frame_delay, self.update)
