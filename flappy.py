import tkinter as tk
from tkinter import messagebox
import random
import json
import os

# Game constants - will be set based on screen size
GRAVITY = 0.6
FLAP_STRENGTH = -12
PIPE_SPEED = 4
PIPE_GAP = 180
PIPE_WIDTH = 70
PIPE_SPAWN_INTERVAL = 1400
BIRD_SIZE = 34
GROUND_HEIGHT = 60

class FlappyBird:
    def __init__(self, root):
        self.root = root
        self.root.title("Flappy Bird - Full Screen Edition")

        # Get screen dimensions
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()

        # Full screen mode
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")

        # Game dimensions (use full screen)
        self.WIDTH = self.screen_width
        self.HEIGHT = self.screen_height

        # High score file
        self.score_file = "flappy_highscore.json"
        self.high_score = self.load_high_score()

        # Main canvas (full screen)
        self.canvas = tk.Canvas(root, width=self.WIDTH, height=self.HEIGHT, 
                                bg="#4EC0CA", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # UI Frame (top-left corner)
        self.ui_frame = tk.Frame(root, bg="#4EC0CA")
        self.ui_frame.place(x=20, y=20)

        self.score_label = tk.Label(self.ui_frame, text="Score: 0", 
                                    font=("Arial", 24, "bold"), bg="#4EC0CA", fg="white")
        self.score_label.pack(side=tk.LEFT, padx=10)

        self.high_label = tk.Label(self.ui_frame, text="High: " + str(self.high_score), 
                                   font=("Arial", 24, "bold"), bg="#4EC0CA", fg="yellow")
        self.high_label.pack(side=tk.LEFT, padx=10)

        # Full screen hint
        self.hint_label = tk.Label(root, text="Press F11 to toggle full screen | ESC to quit", 
                                   font=("Arial", 12), bg="#4EC0CA", fg="white")
        self.hint_label.place(x=self.WIDTH - 350, y=20)

        # Game state
        self.score = 0
        self.game_running = False
        self.game_over = False

        # Bird properties (centered horizontally)
        self.bird_x = self.WIDTH // 4
        self.bird_y = self.HEIGHT // 2
        self.bird_velocity = 0

        # Pipes list
        self.pipes = []

        # Ground
        self.ground_y = self.HEIGHT - GROUND_HEIGHT
        self.draw_ground()

        # Draw bird
        self.draw_bird()

        # Background clouds (decorative)
        self.draw_clouds()

        # Show start screen
        self.show_start_screen()

        # Bind keys
        self.root.bind("<space>", self.flap)
        self.root.bind("<Button-1>", self.flap)
        self.root.bind("<Return>", self.start_game)
        self.root.bind("<r>", self.restart_game)
        self.root.bind("<R>", self.restart_game)
        self.root.bind("<Escape>", self.quit_game)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Configure>", self.on_resize)

        # Animation loop
        self.animate()

    def load_high_score(self):
        if os.path.exists(self.score_file):
            try:
                with open(self.score_file, "r") as f:
                    data = json.load(f)
                    return data.get("high_score", 0)
            except:
                return 0
        return 0

    def save_high_score(self):
        try:
            with open(self.score_file, "w") as f:
                json.dump({"high_score": self.high_score}, f)
        except:
            pass

    def draw_ground(self):
        # Main ground
        self.canvas.create_rectangle(0, self.ground_y, self.WIDTH, self.HEIGHT, 
                                     fill="#DED895", outline="#DED895", tags="ground")
        # Ground top line
        self.canvas.create_line(0, self.ground_y, self.WIDTH, self.ground_y, 
                               width=4, fill="#CBB26A", tags="ground")
        # Ground texture lines
        for i in range(0, self.WIDTH, 40):
            self.canvas.create_line(i, self.ground_y + 10, i + 20, self.ground_y + 10,
                                   fill="#CBB26A", width=2, tags="ground")
            self.canvas.create_line(i + 10, self.ground_y + 25, i + 30, self.ground_y + 25,
                                   fill="#CBB26A", width=2, tags="ground")
            self.canvas.create_line(i + 5, self.ground_y + 40, i + 25, self.ground_y + 40,
                                   fill="#CBB26A", width=2, tags="ground")

    def draw_clouds(self):
        # Draw some decorative clouds in background
        cloud_positions = [
            (self.WIDTH * 0.1, self.HEIGHT * 0.15),
            (self.WIDTH * 0.4, self.HEIGHT * 0.1),
            (self.WIDTH * 0.7, self.HEIGHT * 0.2),
            (self.WIDTH * 0.85, self.HEIGHT * 0.08),
        ]
        for cx, cy in cloud_positions:
            self.draw_cloud(cx, cy)

    def draw_cloud(self, x, y):
        # Simple cloud made of overlapping circles
        r = 25
        self.canvas.create_oval(x - r*2, y - r, x, y + r, 
                               fill="white", outline="white", tags="cloud")
        self.canvas.create_oval(x - r, y - r*1.5, x + r, y + r*0.5, 
                               fill="white", outline="white", tags="cloud")
        self.canvas.create_oval(x, y - r, x + r*2, y + r, 
                               fill="white", outline="white", tags="cloud")

    def draw_bird(self):
        # Bird body
        self.bird = self.canvas.create_oval(
            self.bird_x - BIRD_SIZE//2, self.bird_y - BIRD_SIZE//2,
            self.bird_x + BIRD_SIZE//2, self.bird_y + BIRD_SIZE//2,
            fill="#FFD700", outline="#FFA500", width=2, tags="bird"
        )
        # Eye
        self.eye = self.canvas.create_oval(
            self.bird_x + 6, self.bird_y - 10,
            self.bird_x + 14, self.bird_y - 2,
            fill="white", outline="black", tags="bird"
        )
        # Pupil
        self.pupil = self.canvas.create_oval(
            self.bird_x + 9, self.bird_y - 7,
            self.bird_x + 13, self.bird_y - 3,
            fill="black", tags="bird"
        )
        # Beak
        self.beak = self.canvas.create_polygon(
            self.bird_x + 12, self.bird_y + 2,
            self.bird_x + 26, self.bird_y + 7,
            self.bird_x + 12, self.bird_y + 12,
            fill="#FF6347", outline="#CC3300", tags="bird"
        )
        # Wing
        self.wing = self.canvas.create_oval(
            self.bird_x - 10, self.bird_y + 2,
            self.bird_x + 6, self.bird_y + 14,
            fill="#FFA500", outline="#FF8C00", tags="bird"
        )

    def show_start_screen(self):
        # Title
        self.start_text = self.canvas.create_text(
            self.WIDTH//2, self.HEIGHT//3,
            text="FLAPPY BIRD",
            font=("Arial", 72, "bold"),
            fill="white",
            tags="start"
        )
        # Instructions
        self.instruction_text = self.canvas.create_text(
            self.WIDTH//2, self.HEIGHT//2,
            text="Press SPACE or Click to flap\nPress ENTER to start",
            font=("Arial", 28),
            fill="white",
            tags="start"
        )
        # High score
        self.high_score_text = self.canvas.create_text(
            self.WIDTH//2, self.HEIGHT//2 + 80,
            text="High Score: " + str(self.high_score),
            font=("Arial", 32, "bold"),
            fill="yellow",
            tags="start"
        )
        # Controls hint
        self.controls_text = self.canvas.create_text(
            self.WIDTH//2, self.HEIGHT - 100,
            text="Controls: SPACE = Flap | ENTER = Start | R = Restart | ESC = Quit | F11 = Toggle Full Screen",
            font=("Arial", 16),
            fill="white",
            tags="start"
        )

    def hide_start_screen(self):
        self.canvas.delete("start")

    def start_game(self, event=None):
        if self.game_running or self.game_over:
            return
        self.hide_start_screen()
        self.game_running = True
        self.spawn_pipe()
        self.schedule_next_pipe()

    def flap(self, event=None):
        if not self.game_running and not self.game_over:
            self.start_game()
            return
        if self.game_running and not self.game_over:
            self.bird_velocity = FLAP_STRENGTH

    def spawn_pipe(self):
        if not self.game_running:
            return

        min_gap = 120
        max_gap = self.ground_y - 120
        gap_y = random.randint(min_gap, max_gap)

        # Top pipe
        top_pipe = self.canvas.create_rectangle(
            self.WIDTH, 0, self.WIDTH + PIPE_WIDTH, gap_y - PIPE_GAP//2,
            fill="#73BF2E", outline="#558B1E", width=2, tags="pipe"
        )
        # Top pipe cap
        top_cap = self.canvas.create_rectangle(
            self.WIDTH - 6, gap_y - PIPE_GAP//2 - 24, 
            self.WIDTH + PIPE_WIDTH + 6, gap_y - PIPE_GAP//2,
            fill="#73BF2E", outline="#558B1E", width=2, tags="pipe"
        )
        # Top cap detail
        top_cap_detail = self.canvas.create_rectangle(
            self.WIDTH - 3, gap_y - PIPE_GAP//2 - 20, 
            self.WIDTH + PIPE_WIDTH + 3, gap_y - PIPE_GAP//2 - 4,
            fill="#85D13A", outline="", tags="pipe"
        )

        # Bottom pipe
        bottom_pipe = self.canvas.create_rectangle(
            self.WIDTH, gap_y + PIPE_GAP//2, 
            self.WIDTH + PIPE_WIDTH, self.ground_y,
            fill="#73BF2E", outline="#558B1E", width=2, tags="pipe"
        )
        # Bottom pipe cap
        bottom_cap = self.canvas.create_rectangle(
            self.WIDTH - 6, gap_y + PIPE_GAP//2,
            self.WIDTH + PIPE_WIDTH + 6, gap_y + PIPE_GAP//2 + 24,
            fill="#73BF2E", outline="#558B1E", width=2, tags="pipe"
        )
        # Bottom cap detail
        bottom_cap_detail = self.canvas.create_rectangle(
            self.WIDTH - 3, gap_y + PIPE_GAP//2 + 4, 
            self.WIDTH + PIPE_WIDTH + 3, gap_y + PIPE_GAP//2 + 20,
            fill="#85D13A", outline="", tags="pipe"
        )

        self.pipes.append([top_pipe, top_cap, top_cap_detail, 
                          bottom_pipe, bottom_cap, bottom_cap_detail, 
                          self.WIDTH, gap_y, False])

    def schedule_next_pipe(self):
        if self.game_running:
            self.root.after(PIPE_SPAWN_INTERVAL, self.spawn_pipe)
            self.root.after(PIPE_SPAWN_INTERVAL, self.schedule_next_pipe)

    def update_bird(self):
        self.bird_velocity += GRAVITY
        self.bird_y += self.bird_velocity

        self.canvas.coords(self.bird,
            self.bird_x - BIRD_SIZE//2, self.bird_y - BIRD_SIZE//2,
            self.bird_x + BIRD_SIZE//2, self.bird_y + BIRD_SIZE//2)
        self.canvas.coords(self.eye,
            self.bird_x + 6, self.bird_y - 10,
            self.bird_x + 14, self.bird_y - 2)
        self.canvas.coords(self.pupil,
            self.bird_x + 9, self.bird_y - 7,
            self.bird_x + 13, self.bird_y - 3)
        self.canvas.coords(self.beak,
            self.bird_x + 12, self.bird_y + 2,
            self.bird_x + 26, self.bird_y + 7,
            self.bird_x + 12, self.bird_y + 12)
        self.canvas.coords(self.wing,
            self.bird_x - 10, self.bird_y + 2,
            self.bird_x + 6, self.bird_y + 14)

    def update_pipes(self):
        for pipe in self.pipes:
            pipe[6] -= PIPE_SPEED

            x = pipe[6]
            gap_y = pipe[7]

            self.canvas.coords(pipe[0], x, 0, x + PIPE_WIDTH, gap_y - PIPE_GAP//2)
            self.canvas.coords(pipe[1], x - 6, gap_y - PIPE_GAP//2 - 24, 
                              x + PIPE_WIDTH + 6, gap_y - PIPE_GAP//2)
            self.canvas.coords(pipe[2], x - 3, gap_y - PIPE_GAP//2 - 20, 
                              x + PIPE_WIDTH + 3, gap_y - PIPE_GAP//2 - 4)
            self.canvas.coords(pipe[3], x, gap_y + PIPE_GAP//2, 
                              x + PIPE_WIDTH, self.ground_y)
            self.canvas.coords(pipe[4], x - 6, gap_y + PIPE_GAP//2,
                              x + PIPE_WIDTH + 6, gap_y + PIPE_GAP//2 + 24)
            self.canvas.coords(pipe[5], x - 3, gap_y + PIPE_GAP//2 + 4,
                              x + PIPE_WIDTH + 3, gap_y + PIPE_GAP//2 + 20)

            if not pipe[8] and x + PIPE_WIDTH < self.bird_x:
                pipe[8] = True
                self.score += 1
                self.score_label.config(text="Score: " + str(self.score))

                if self.score > self.high_score:
                    self.high_score = self.score
                    self.high_label.config(text="High: " + str(self.high_score))
                    self.save_high_score()

    def check_collision(self):
        if self.bird_y + BIRD_SIZE//2 >= self.ground_y:
            return True

        if self.bird_y - BIRD_SIZE//2 <= 0:
            return True

        bird_left = self.bird_x - BIRD_SIZE//2 + 5
        bird_right = self.bird_x + BIRD_SIZE//2 - 5
        bird_top = self.bird_y - BIRD_SIZE//2 + 5
        bird_bottom = self.bird_y + BIRD_SIZE//2 - 5

        for pipe in self.pipes:
            x = pipe[6]
            gap_y = pipe[7]

            if bird_right > x and bird_left < x + PIPE_WIDTH:
                if bird_top < gap_y - PIPE_GAP//2 or bird_bottom > gap_y + PIPE_GAP//2:
                    return True

        return False

    def clean_pipes(self):
        new_pipes = []
        for pipe in self.pipes:
            if pipe[6] + PIPE_WIDTH > -50:
                new_pipes.append(pipe)
            else:
                for i in range(6):
                    self.canvas.delete(pipe[i])
        self.pipes = new_pipes

    def game_over_screen(self):
        self.game_over = True
        self.game_running = False

        self.save_high_score()

        self.canvas.create_rectangle(0, 0, self.WIDTH, self.HEIGHT, 
                                     fill="black", stipple="gray50", tags="gameover")

        self.canvas.create_text(
            self.WIDTH//2, self.HEIGHT//3,
            text="GAME OVER",
            font=("Arial", 72, "bold"),
            fill="red",
            tags="gameover"
        )

        self.canvas.create_text(
            self.WIDTH//2, self.HEIGHT//2 - 30,
            text="Score: " + str(self.score),
            font=("Arial", 36),
            fill="white",
            tags="gameover"
        )

        new_record = self.score >= self.high_score and self.score > 0
        record_text = "NEW RECORD!" if new_record else "High Score: " + str(self.high_score)
        record_color = "gold" if new_record else "yellow"

        self.canvas.create_text(
            self.WIDTH//2, self.HEIGHT//2 + 20,
            text=record_text,
            font=("Arial", 32, "bold"),
            fill=record_color,
            tags="gameover"
        )

        self.canvas.create_text(
            self.WIDTH//2, self.HEIGHT//2 + 100,
            text="Press R to restart\nPress ESC to quit",
            font=("Arial", 24),
            fill="white",
            tags="gameover"
        )

    def restart_game(self, event=None):
        if not self.game_over:
            return

        self.canvas.delete("all")

        self.score = 0
        self.score_label.config(text="Score: 0")
        self.high_label.config(text="High: " + str(self.high_score))
        self.game_running = False
        self.game_over = False
        self.bird_y = self.HEIGHT // 2
        self.bird_velocity = 0
        self.pipes = []

        self.draw_ground()
        self.draw_clouds()
        self.draw_bird()
        self.show_start_screen()

    def toggle_fullscreen(self, event=None):
        is_full = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not is_full)
        return "break"

    def on_resize(self, event=None):
        # Update dimensions on resize
        self.WIDTH = self.root.winfo_width()
        self.HEIGHT = self.root.winfo_height()
        self.ground_y = self.HEIGHT - GROUND_HEIGHT

    def quit_game(self, event=None):
        self.save_high_score()
        self.root.destroy()

    def animate(self):
        if self.game_running and not self.game_over:
            self.update_bird()
            self.update_pipes()
            self.clean_pipes()

            if self.check_collision():
                self.game_over_screen()

        self.root.after(16, self.animate)

def main():
    root = tk.Tk()
    game = FlappyBird(root)
    root.mainloop()

if __name__ == "__main__":
    main()