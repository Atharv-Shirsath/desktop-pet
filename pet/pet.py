import tkinter as tk
import time
import random
import winsound

class Pet:
    def __init__(self):
        self.window = tk.Tk()
        print("Pet initializing...")

        # CONFIG
        self.scale = 3
        self.frame_delay = 100  # ms per frame

        # LOAD ANIMATIONS
        self.anims = {
            "idle_right": self.load_gif("assets/gifs/idle_right.gif"),
            "idle_left": self.load_gif("assets/gifs/idle_left.gif"),
            "standing_up_idle_right": self.load_gif(
                "assets/gifs/standing_up_idle_right.gif"
            ),
            "standing_up_idle_left": self.load_gif(
                "assets/gifs/standing_up_idle_left.gif"
            ),
            "standing_up_idle_1_right": self.load_gif(
                "assets/gifs/standing_up_idle_1_right.gif"
            ),
            "standing_up_idle_1_left": self.load_gif(
                "assets/gifs/standing_up_idle_1_left.gif"
            ),
            "sit_down_right": self.load_gif("assets/gifs/sit_down_right.gif"),
            "sit_down_left": self.load_gif("assets/gifs/sit_down_left.gif"),
            "napping": self.load_gif("assets/gifs/napping.gif"),
            "looking_around_napping": self.load_gif(
                "assets/gifs/looking_around_while_napping.gif"
            ),
            "stand_up_right": self.load_gif("assets/gifs/stand_up_right.gif"),
            "stand_up_left": self.load_gif("assets/gifs/stand_up_left.gif"),
            "run_right": self.load_gif("assets/gifs/running_right.gif"),
            "run_left": self.load_gif("assets/gifs/running_left.gif"),
            "fast_run_right": self.load_gif("assets/gifs/fast_running_right.gif"),
            "fast_run_left": self.load_gif("assets/gifs/fast_running_left.gif"),
            "walk_2_right": self.load_gif("assets/gifs/walking_on_2_legs_right.gif"),
            "walk_2_left": self.load_gif("assets/gifs/walking_on_2_legs_left.gif"),
            "stop_right": self.load_gif("assets/gifs/running_stop_right.gif"),
            "stop_left": self.load_gif("assets/gifs/running_stop_left.gif"),
            "angry_right": self.load_gif("assets/gifs/angry_right.gif"),
            "angry_left": self.load_gif("assets/gifs/angry_left.gif"),
        }

        self.horizontal_dir = 1  # 1:right, -1:left
        self.vertical_dir = 0  # vertical movement disabled for horizontal-only

        self.state = "idle_right"
        self.frames = self.anims[self.state]
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
        self.sound_interval = random.randint(1200, 1800)  # 14–17 minutes (in seconds)

        self.update()
        self.window.mainloop()

    def play_meow(self):
        try:
            winsound.PlaySound("assets/sounds/meow.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
        except:
            print("Missing meow.wav")

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

    def get_direction_suffix(self):
        return "_right" if self.horizontal_dir == 1 else "_left"

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
        sfx = self.get_direction_suffix()
        self.state = f"angry{sfx}"
        self.frames = self.anims[self.state]
        self.frame_idx = 0
        self.start_time = time.time()
        self.duration = 3
        self.angry_until = time.time() + self.duration
        self.vertical_dir = 0

    def transition(self):
        # If angry duration not over, do not transition
        if time.time() < self.angry_until:
            return

        sfx = self.get_direction_suffix()
        curr = self.state

        if any(x in curr for x in ["sit_down", "stand_up", "stop"]):
            self.state = f"idle{sfx}"
            self.duration = random.randint(4, 8)
            self.vertical_dir = 0

        elif "napping" in curr:
            self.vertical_dir = 0
            if random.random() < 0.2:
                self.state = f"stand_up{sfx}"
                self.duration = 0
            else:
                self.state = (
                    "looking_around_napping" if random.random() < 0.4 else "napping"
                )
                self.duration = 8

        elif "idle" in curr:
            rand = random.random()
            if rand < 0.5:
                if random.random() < 0.3:
                    self.horizontal_dir *= -1
                new_sfx = self.get_direction_suffix()

                self.vertical_dir = 0
                self.state = random.choice(
                    [f"run{new_sfx}", f"walk_2{new_sfx}", f"fast_run{new_sfx}"]
                )
                self.duration = random.randint(5, 10)

            elif rand < 0.7:
                self.vertical_dir = 0
                if random.random() < 0.7:
                    self.state = f"sit_down{sfx}"
                    self.duration = 0
                else:
                    self.state = "napping"
                    self.duration = 10

            else:
                self.vertical_dir = 0
                self.state = f"standing_up_idle_1{sfx}"
                self.duration = 5

        elif any(x in curr for x in ["run", "walk"]):
            if random.random() < 0.4:
                self.state = f"stop{sfx}"
                self.duration = 0
                self.vertical_dir = 0
            else:
                self.vertical_dir = 0
                self.duration = random.randint(3, 6)

        else:
            self.state = f"idle{sfx}"
            self.duration = 5
            self.vertical_dir = 0

        self.frames = self.anims.get(self.state, self.anims[f"idle{sfx}"])
        self.frame_idx = 0
        self.start_time = time.time()

    def update(self):
        if self.dragging:
            # Dragging logic unchanged
            if self.frames:
                self.label.config(image=self.frames[self.frame_idx])
                self.frame_idx = (self.frame_idx + 1) % len(self.frames)
            self.window.geometry(f"+{int(self.x)}+{int(self.y)}")
            self.window.after(self.frame_delay, self.update)
            return

        now = time.time()
        # Timed sound
        if now - self.last_sound_time > self.sound_interval:
            self.play_meow()
            self.last_sound_time = now
            self.sound_interval = random.randint(1200, 1800)

        # Angry state priority
        if now < self.angry_until:
            if not ("angry_right" in self.state or "angry_left" in self.state):
                sfx = self.get_direction_suffix()
                self.state = f"angry{sfx}"
                self.frames = self.anims[self.state]
                self.frame_idx = 0
                self.start_time = now
            self.vertical_dir = 0
            if self.frames:
                self.label.config(image=self.frames[self.frame_idx])
                self.frame_idx = (self.frame_idx + 1) % len(self.frames)
            self.window.geometry(f"+{int(self.x)}+{int(self.y)}")
            self.window.after(self.frame_delay, self.update)
            return

        # Movement speed map (pixels per update)
        speed_map = {
            "fast_run": 6,
            "run": 3,
            "walk_2": 1,
        }
        speed = 0
        for key, val in speed_map.items():
            if key in self.state:
                speed = val
                break

        # Move horizontally by speed pixels per update
        self.x += speed * self.horizontal_dir

        pet_w = self.frames[0].width()
        pet_h = self.frames[0].height()

        hit_wall = False

        if self.x < 0:
            self.x = 5
            self.horizontal_dir = 1
            hit_wall = True
        elif self.x > self.screen_w - pet_w:
            self.x = self.screen_w - pet_w - 5
            self.horizontal_dir = -1
            hit_wall = True

        if hit_wall:
            sfx = self.get_direction_suffix()
            if f"stop{sfx}" in self.anims:
                self.state = f"stop{sfx}"
            else:
                self.state = f"idle{sfx}"
            self.frames = self.anims[self.state]
            self.frame_idx = 0
            self.start_time = now
            self.duration = 0
            self.vertical_dir = 0

        if self.frames:
            self.label.config(image=self.frames[self.frame_idx])
            self.frame_idx = (self.frame_idx + 1) % len(self.frames)
        else:
            print(f"Error: No frames for state {self.state}")

        self.window.geometry(f"+{int(self.x)}+{int(self.y)}")

        # Only transition if not angry
        if now >= self.angry_until:
            time_passed = now - self.start_time
            if (self.duration == 0 and self.frame_idx == 0) or (
                self.duration > 0 and time_passed > self.duration
            ):
                self.transition()

        self.window.after(self.frame_delay, self.update)
