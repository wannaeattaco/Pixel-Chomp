"""Game controller class"""
import tkinter as tk
import turtle
import copy
import time
import os
from datetime import datetime
from maze_layout import LAYOUTS
from PacMan import PacMan
from Ghost import Ghost
from StatisticsManager import StatisticsManager
from Maze import Maze

DIFFICULTY_SETTINGS = {
    "easy": {"ghost_count": 2, "ghost_speed": 4, "power_duration": 100},
    "normal": {"ghost_count": 3, "ghost_speed": 3, "power_duration": 60},
    "hard": {"ghost_count": 4, "ghost_speed": 3, "power_duration": 40},
}


class GameController:
    """Manages game state"""

    def __init__(self, status_writer):
        self.game_state = 'menu'
        self.score = 0
        self.timer = 0
        self.game_mode = 'easy'
        self.stats_manager = StatisticsManager()
        self.status_writer = status_writer
        self.status_message = None
        self.maze = None
        self.pacman = None
        self.ghosts = []
        self.drawer = None
        self.first_move_done = False
        self.btn_style = {
            "font": ("Arial", 16, "bold"),
            "bg": "#393938",
            "fg": "#393938",
            "activebackground": "#393938",
            "activeforeground": "#393938",
            "relief": tk.FLAT,
            "bd": 0,
            "width": 15,
            "height": 2
        }

    def setup_window(self, title, size='700x700'):
        """Setup common window properties"""
        win = tk.Tk()
        win.title(title)
        win.configure(bg='black')
        win.geometry(size)
        return win

    def on_play(self, root):
        """Handle play button click"""
        root.destroy()
        self.set_difficulty()

    def on_stats(self, root):
        """Handle stats button click"""
        root.destroy()
        self.stats_manager.show_graph_selector(back_callback=self.show_main_menu,
                                               btn_style=self.btn_style)

    def on_how_to_play(self, root):
        """Handle how to play button click"""
        root.destroy()
        self.show_how_to_play()

    def on_quit(self):
        """Handle quit button click"""
        os._exit(0)

    def show_main_menu(self):
        """Show main menu"""
        root = self.setup_window("Pixel Chomp - Main Menu")
        title = tk.Label(root, text="Pixel Chomp", font=("Arial", 40, "bold"),
                         bg="black", fg="white")
        title.pack(pady=30)

        tk.Button(root, text="PLAY", command=lambda: self.on_play(root),
                  **self.btn_style).pack(pady=10)
        tk.Button(root, text="STATS", command=lambda: self.on_stats(root),
                  **self.btn_style).pack(pady=10)
        tk.Button(root, text="HOW TO PLAY", command=lambda: self.on_how_to_play(root),
                  **self.btn_style).pack(pady=10)
        tk.Button(root, text="QUIT", command=self.on_quit, **self.btn_style).pack(pady=10)
        root.mainloop()

    def start_game_and_close(self, diff_root, difficulty):
        """Start game and close difficulty menu"""
        diff_root.destroy()
        self.start_game(difficulty)
        self.setup_controls(self.screen)
        self.update_game_state(self.screen)

    def go_back_to_main(self, diff_root):
        """Go back to main menu"""
        diff_root.destroy()
        self.show_main_menu()

    def set_difficulty(self):
        """Show difficulty selection menu"""
        diff_root = self.setup_window("Select Difficulty")
        label = tk.Label(diff_root, text="Select Difficulty", font=("Arial", 24, "bold"),
                         bg="black", fg="white")
        label.pack(pady=30)

        for diff in ["Easy", "Normal", "Hard"]:
            tk.Button(diff_root, text=diff.upper(),
                     command=lambda d=diff.lower(): self.start_game_and_close(diff_root, d),
                     **self.btn_style).pack(pady=10)
        tk.Button(diff_root, text="BACK", command=lambda: self.go_back_to_main(diff_root),
                  **self.btn_style).pack(pady=10)
        tk.Button(diff_root, text="QUIT", command=self.on_quit, **self.btn_style).pack(pady=10)
        diff_root.mainloop()

    def update_status(self, score, lives, timer):
        """Function for update status when play game"""
        try:
            if hasattr(self.status_writer.screen, 'cv') and \
            self.status_writer.screen.cv.winfo_exists():
                self.status_writer.clear()
                self.status_writer.goto(-230, 260)
                self.status_writer.write(
                    f"Score: {score}    Lives: {lives}    Time: {timer}s",
                    font=("Arial", 16, "bold"))
        except (turtle.TurtleGraphicsError, Exception):
            pass

    def game_over_screen(self, win=True):
        """Make 'game over' text appear on screen"""
        self.clear_status_message()
        self.status_message = turtle.Turtle()
        self.status_message.hideturtle()
        self.status_message.color("white")
        self.status_message.penup()
        self.status_message.goto(0, 0)
        msg = "YOU WIN!" if win else "GAME OVER"
        try:
            if hasattr(self.status_message.screen, 'cv') and \
            self.status_message.screen.cv.winfo_exists():
                self.status_message.write(
                    f"{msg}\nPress R to Restart\nPress Q for Main Menu",
                    align="center", font=("Arial", 30, "bold"))
        except (turtle.TurtleGraphicsError, Exception):
            pass

    def clear_status_message(self):
        """Clear status message that appear on screen"""
        if self.status_message:
            try:
                if hasattr(self.status_message.screen, 'cv') and \
                self.status_message.screen.cv.winfo_exists():
                    self.status_message.clear()
                    self.status_message.hideturtle()
            except (turtle.TurtleGraphicsError, Exception):
                pass
            self.status_message = None

    def start_game(self, difficulty):
        """Start the game"""
        self.game_state = 'running'
        self.game_mode = difficulty
        self.timer = 0
        self.first_move_done = False
        self.maze = Maze(difficulty)
        self.maze.layout = copy.deepcopy(LAYOUTS[difficulty])
        self.screen = turtle.Screen()
        self.screen.bgcolor("black")
        self.screen.tracer(0)
        self.drawer = turtle.Turtle()
        self.drawer.shape('square')
        self.drawer.penup()
        self.drawer.speed(0)
        self.maze.load_maze(self.drawer)
        self.pacman = PacMan(self.maze, DIFFICULTY_SETTINGS[difficulty])
        self.ghosts = []
        ghost_count = DIFFICULTY_SETTINGS[difficulty]["ghost_count"]
        colors = ['red', 'cyan', 'orange', 'pink']
        spawns = self.maze.ghost_spawns
        for i in range(ghost_count):
            spawn = spawns[i % len(spawns)]
            ghost = Ghost(self.maze, colors[i % len(colors)], spawn=spawn)
            self.ghosts.append(ghost)
        self.screen.update()

    def setup_controls(self, screen):
        """Setup controls for the game"""
        def record_first_move():
            if not self.first_move_done:
                self.stats_manager.record_timestamp(datetime.now().isoformat(), self.pacman)
                self.stats_manager.record_data(self.pacman, 0, self.game_mode)
                self.stats_manager.save_to_file()
                self.first_move_done = True

        def move_up():
            self.pacman.move(0, -1, self.drawer)
            record_first_move()

        def move_down():
            self.pacman.move(0, 1, self.drawer)
            record_first_move()

        def move_left():
            self.pacman.move(-1, 0, self.drawer)
            record_first_move()

        def move_right():
            self.pacman.move(1, 0, self.drawer)
            record_first_move()

        screen.listen()
        screen.onkeypress(move_up, "Up")
        screen.onkeypress(move_down, "Down")
        screen.onkeypress(move_left, "Left")
        screen.onkeypress(move_right, "Right")
        screen.onkeypress(lambda: self.restart(screen), "r")
        screen.onkeypress(lambda: self.quit_to_main(screen), "q")

    def check_win_condition(self):
        """Check if the game is won"""
        return all(cell not in (1, 2) for row in self.maze.layout for cell in row)

    def update_game_state(self, screen):
        """Main game loop"""
        if self.game_state != 'running':
            return

        self.timer += 1
        self.pacman.change_state()
        self.update_status(self.pacman.score, self.pacman.lives, self.timer // 10)
        if self.timer % DIFFICULTY_SETTINGS[self.game_mode]["ghost_speed"] == 0:
            for ghost in self.ghosts:
                ghost.move(self.pacman.x, self.pacman.y, self.pacman.state == "powered")
        for ghost in self.ghosts:
            if ghost.x == self.pacman.x and ghost.y == self.pacman.y:
                if self.pacman.state == 'powered' and self.pacman.eat_ghost():
                    ghost.respawn()
                else:
                    self.pacman.lives -= 1
                    self.pacman.x, self.pacman.y = self.pacman.maze.pacman_start
                    self.pacman.update_position()
                    for g in self.ghosts:
                        g.respawn()
                    time.sleep(1)
        for ghost in self.ghosts:
            ghost.update_position(
                powered=self.pacman.state == "powered",
                power_timer=self.pacman.power_timer,
                power_duration=self.pacman.settings["power_duration"]
            )
        if self.timer % 100 == 0:
            self.stats_manager.record_timestamp(datetime.now().isoformat(), self.pacman)
        if self.timer % 50 == 0:
            self.stats_manager.record_data(self.pacman, self.timer // 10, self.game_mode)
            self.stats_manager.save_to_file()
        screen.update()
        time.sleep(0.1)
        if self.check_win_condition() or self.pacman.lives <= 0:
            self.game_state = 'game_over'
            self.clear_status_message()
            self.stats_manager.record_timestamp(datetime.now().isoformat(), self.pacman)
            self.stats_manager.record_data(self.pacman, self.timer // 10, self.game_mode)
            self.stats_manager.save_to_file()
            if self.check_win_condition():
                self.game_over_screen(win=True)
            else:
                self.game_over_screen(win=False)
            print(self.stats_manager.generate_report())
            screen.onkeypress(self.restart, "r")
            screen.listen()

        if self.game_state == 'running':
            screen.ontimer(lambda: self.update_game_state(screen), 100)

    def restart(self, screen=None):
        """Restart the game"""
        if screen is None:
            screen = self.screen
        try:
            for t in turtle.turtles():
                t.hideturtle()
                t.clear()
        except turtle.TurtleGraphicsError:
            pass
        screen.bgcolor("black")
        screen.tracer(0)
        self.start_game(self.game_mode)
        self.setup_controls(screen)
        self.update_game_state(screen)

    def quit_to_main(self, screen):
        """Quit to main menu"""
        screen.clearscreen()
        self.show_main_menu()

    def show_how_to_play(self):
        """Show how to play screen"""
        win = tk.Tk()
        win.title("How to Play - Pixel Chomp")
        win.configure(bg='black')
        win.geometry('700x700')

        instructions = (
            "HOW TO PLAY\n\n"
            "- Use the ARROW KEYS to move.\n"
            "- Eat all the white dots to win the level.\n"
            "- Avoid the ghosts or lose a life!\n"
            "- Eat a big dot (power pellet) to turn ghosts blue and"
            "     chomp them for bonus points!\n"
            "- You start withonly have 3 lives.\n"
            "- Press R to restart after game over.\n"
            "- Press Q to return to the main menu.\n\n\n"
            "DIFFICULTY LEVELS:\n\n"
            "- EASY:     2 ghosts, slower speed, long power pellet duration.\n"
            "- NORMAL:   3 ghosts, balanced speed, standard power duration.\n"
            "- HARD:     4 ghosts, fast speed, short power duration.\n\n"
            "Choose wisely and aim for the high score!\n\n"
            "Good luck, Chomper!"
        )

        label = tk.Label(
            win, text=instructions, bg='black',
            font=("Arial", 15), justify='left'
        )
        label.pack(pady=30)

        def back():
            win.destroy()
            self.show_main_menu()

        tk.Button(win, text="BACK", command=back, **self.btn_style).pack(pady=20)
        win.mainloop()
