"""Pixel Chomp"""
import turtle
import time
import random
import heapq
import csv
from datetime import datetime
from maze_layout import LAYOUTS

TILE_SIZE = 24
DIFFICULTY_SETTINGS = {
    "easy": {"ghost_count": 2, "ghost_speed": 4, "power_duration": 100},
    "normal": {"ghost_count": 3, "ghost_speed": 3, "power_duration": 60},
    "hard": {"ghost_count": 4, "ghost_speed": 3, "power_duration": 30},
}


class Maze:
    """Represents the game maze with walls, dots, and power pellets"""

    def __init__(self, difficulty="easy"):
        """Initialize maze with given difficulty level"""
        self.layout = LAYOUTS[difficulty]
        self.pacman_start = None
        self.ghost_spawns = []
        for y, row in enumerate(self.layout):
            for x, val in enumerate(row):
                if val == 4:
                    self.pacman_start = (x, y)
                elif val == 5:
                    self.ghost_spawns.append((x, y))

    def is_wall(self, x, y):
        """Check if given coordinates contain a wall"""
        try:
            return self.layout[y][x] == 0
        except IndexError:
            return True

    def draw(self, drawer):
        """Draw the maze"""
        drawer.hideturtle()
        drawer.speed(0)
        for y, row in enumerate(self.layout):
            for x, val in enumerate(row):
                sx = -252 + (x * TILE_SIZE)
                sy = 252 - (y * TILE_SIZE)
                drawer.penup()
                drawer.goto(sx, sy)
                if val == 0:
                    drawer.color('blue', 'blue')
                    drawer.begin_fill()
                    for _ in range(4):
                        drawer.forward(TILE_SIZE)
                        drawer.right(90)
                    drawer.end_fill()
                elif val == 1:
                    drawer.goto(sx + TILE_SIZE / 2, sy - TILE_SIZE / 2)
                    drawer.dot(6, 'white')
                elif val == 2:
                    drawer.goto(sx + TILE_SIZE / 2, sy - TILE_SIZE / 2)
                    drawer.dot(12, 'white')


class PacMan:
    """Represents the player with movement and state management"""

    def __init__(self, maze, settings):
        """Initialize Pac-Man"""
        self.maze = maze
        self.settings = settings
        self.x, self.y = maze.pacman_start
        self.icon = turtle.Turtle()
        self.icon.shape('circle')
        self.icon.color('yellow')
        self.icon.penup()
        self.icon.speed(0)
        self.state = 'normal'
        self.power_timer = 0
        self.lives = 3
        self.score = 0
        self.dots_collected = 0
        self.ghosts_eaten = 0
        self.power_pellets_collected = 0
        self.update_position()

    def power_up(self):
        """Activate power up effects"""
        self.state = 'powered'
        self.power_timer = self.settings["power_duration"]

    def update_power(self):
        """Update power pellet timer and state"""
        if self.state == 'powered':
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.state = 'normal'

    def move(self, dx, dy, drawer=None):
        """Move Pac-Man in given direction if possible"""
        nx, ny = self.x + dx, self.y + dy
        if not self.maze.is_wall(nx, ny):
            val = self.maze.layout[ny][nx]
            if val == 1:
                self.score += 10
                self.dots_collected += 1
                self.maze.layout[ny][nx] = 3
            elif val == 2:
                self.score += 50
                self.power_pellets_collected += 1
                self.maze.layout[ny][nx] = 3
                self.power_up()

            if drawer:
                sx = -252 + (nx * TILE_SIZE)
                sy = 252 - (ny * TILE_SIZE)
                drawer.goto(sx + TILE_SIZE / 2, sy - TILE_SIZE / 2)
                drawer.dot(14 if val == 2 else 8, 'black')

            self.x, self.y = nx, ny
            self.update_position()

    def update_position(self):
        """Update Pac-Man's position on screen"""
        sx = -252 + (self.x * TILE_SIZE)
        sy = 252 - (self.y * TILE_SIZE)
        self.icon.goto(sx + TILE_SIZE // 2, sy - TILE_SIZE // 2)
        self.icon.showturtle()

    def eat_ghost(self):
        """Eat a ghost when powered up"""
        if self.state == 'powered':
            self.ghosts_eaten += 1
            self.score += 200
            return True
        return False


class Ghost:
    """Represents enemy ghosts"""

    def __init__(self, maze, color='red'):
        """Initialize ghost with starting position and color"""
        self.maze = maze
        self.start = random.choice(maze.ghost_spawns)
        self.x, self.y = self.start
        self.original_color = color
        self.icon = turtle.Turtle()
        self.icon.shape('circle')
        self.icon.color(color)
        self.icon.penup()
        self.icon.speed(0)
        self.update_position()

    def a_star_search(self, target_x, target_y):
        """Find path to target using A* algorithm"""
        def heuristic(x, y):
            return abs(x - target_x) + abs(y - target_y)

        open_set = []
        heapq.heappush(open_set,
                      (heuristic(self.x, self.y), self.x, self.y, []))
        visited = set()
        while open_set:
            _, x, y, path = heapq.heappop(open_set)
            if (x, y) == (target_x, target_y):
                return path
            if (x, y) in visited:
                continue
            visited.add((x, y))
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if not self.maze.is_wall(nx, ny):
                    new_path = path + [(dx, dy)]
                    heapq.heappush(open_set,
                                 (heuristic(nx, ny) + len(new_path),
                                 nx, ny, new_path))
        return []

    def move(self, tx, ty, powered):
        """Move ghost toward or away from target based on power state"""
        if powered:
            self.icon.color('blue')
            path = self.a_star_search(2 * self.x - tx, 2 * self.y - ty)
        else:
            self.icon.color(self.original_color)
            path = self.a_star_search(tx, ty)
        if path:
            dx, dy = path[0]
            self.x += dx
            self.y += dy
        self.update_position()

    def update_position(self):
        """Update ghost's position on screen"""
        sx = -252 + (self.x * TILE_SIZE)
        sy = 252 - (self.y * TILE_SIZE)
        self.icon.goto(sx + TILE_SIZE // 2, sy - TILE_SIZE // 2)

    def respawn(self):
        """Return ghost to its starting position"""
        self.x, self.y = self.start
        self.update_position()


class StatisticsManager:
    """Handles recording and reporting game statistics"""

    def __init__(self):
        """Initialize statistics tracking structures"""
        self.player_data = {
            'timestamp': [], 'score': [], 'duration': [],
            'lives_lost': [], 'dots_collected': [],
            'ghosts_eaten': [], 'power_pellets_collected': [],
            'difficulty': []
        }
        self.timestamps = []

    def record_timestamp(self, timestamp, pacman):
        """Record game state at specific time"""
        self.timestamps.append({
            'time': timestamp,
            'score': pacman.score,
            'dots': pacman.dots_collected,
            'ghosts': pacman.ghosts_eaten,
            'lives': pacman.lives
        })

    def record_data(self, pacman, duration, difficulty):
        """Record final game statistics"""
        self.player_data['timestamp'].append(datetime.now().isoformat())
        self.player_data['score'].append(pacman.score)
        self.player_data['duration'].append(duration)
        self.player_data['lives_lost'].append(3 - pacman.lives)
        self.player_data['dots_collected'].append(pacman.dots_collected)
        self.player_data['ghosts_eaten'].append(pacman.ghosts_eaten)
        self.player_data['power_pellets_collected'].append(
            pacman.power_pellets_collected)
        self.player_data['difficulty'].append(difficulty)

    def save_to_file(self, filename='game_stats.csv'):
        """Save statistics to CSV file"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.player_data.keys())
            writer.writeheader()
            for i in range(len(self.player_data['timestamp'])):
                row = {k: self.player_data[k][i] for k in self.player_data}
                writer.writerow(row)

    def generate_report(self):
        """Generate summary report of game statistics"""
        if not self.player_data['score']:
            return "No data available"
        report = "\nGame Performance Report\n" + "=" * 24 + "\n"
        report += f"Sessions: {len(self.player_data['score'])}\n"
        max_score = max(self.player_data['score'])
        avg_score = sum(self.player_data['score']) / len(self.player_data['score'])
        report += f"High Score: {max_score}\n"
        report += f"Avg Score: {avg_score:.1f}\n"
        total_dots = sum(self.player_data['dots_collected'])
        report += f"Total Dots Collected: {total_dots}\n"
        total_ghosts = sum(self.player_data['ghosts_eaten'])
        report += f"Total Ghosts Eaten: {total_ghosts}\n"
        total_pellets = sum(self.player_data['power_pellets_collected'])
        report += f"Total Power Pellets: {total_pellets}\n"
        total_lives = sum(self.player_data['lives_lost'])
        report += f"Total Lives Lost: {total_lives}\n"

        difficulties = set(self.player_data['difficulty'])
        report += "\nDifficulty Breakdown:\n"
        for diff in difficulties:
            count = self.player_data['difficulty'].count(diff)
            report += f"- {diff.capitalize()}: {count} games\n"

        return report


class GameController:
    """Manages game state"""

    def __init__(self):
        """Initialize game controller with default state"""
        self.game_state = 'menu'
        self.score = 0
        self.timer = 0
        self.game_mode = 'easy'
        self.stats_manager = StatisticsManager()
        self.status_writer = turtle.Turtle()
        self.status_writer.color("white")
        self.status_writer.penup()
        self.status_writer.hideturtle()
        self.status_writer.speed(0)
        self.maze = None
        self.pacman = None
        self.ghosts = None
        self.drawer = None

    def update_status(self, score, lives, timer):
        """Update on-screen status"""
        self.status_writer.clear()
        self.status_writer.goto(-230, 260)
        self.status_writer.write(
            f"Score: {score}    Lives: {lives}    Time: {timer}s",
            font=("Arial", 14, "bold"))

    def game_over_screen(self, win=True):
        """Display game over or victory screen"""
        self.status_writer.clear()
        self.status_writer.goto(0, 0)
        msg = "YOU WIN!" if win else "GAME OVER"
        self.status_writer.write(
            msg + "\nPress R to Restart",
            align="center",
            font=("Arial", 24, "bold"))

    def start_game(self, difficulty):
        """Initialize new game with given difficulty"""
        self.game_state = 'running'
        self.game_mode = difficulty
        self.timer = 0
        self.maze = Maze(difficulty)
        self.pacman = PacMan(self.maze, DIFFICULTY_SETTINGS[difficulty])
        colors = ['red', 'cyan', 'orange', 'pink']
        ghost_count = DIFFICULTY_SETTINGS[difficulty]["ghost_count"]
        self.ghosts = [Ghost(self.maze, colors[i % 4]) for i in range(ghost_count)]
        self.drawer = turtle.Turtle()
        self.drawer.shape('square')
        self.drawer.penup()
        self.drawer.speed(0)
        self.maze.draw(self.drawer)

    def setup_controls(self, screen):
        """Set up keyboard controls"""
        def move_up():
            self.pacman.move(0, -1, self.drawer)

        def move_down():
            self.pacman.move(0, 1, self.drawer)

        def move_left():
            self.pacman.move(-1, 0, self.drawer)

        def move_right():
            self.pacman.move(1, 0, self.drawer)

        def restart():
            screen.clear()
            screen.tracer(0)
            self.__init__()
            self.start_game(self.game_mode)
            self.setup_controls(screen)
            self.run_game_loop(screen)

        screen.listen()
        screen.onkeypress(move_up, "Up")
        screen.onkeypress(move_down, "Down")
        screen.onkeypress(move_left, "Left")
        screen.onkeypress(move_right, "Right")
        screen.onkeypress(restart, "r")

    def check_win_condition(self):
        """Check if all dots and pellets have been collected"""
        return all(cell not in (1, 2) for row in self.maze.layout for cell in row)

    def run_game_loop(self, screen):
        """Main game loop handling updates and collisions"""
        running = True
        while running:
            try:
                screen.update()
                time.sleep(0.1)
                self.timer += 1
                self.pacman.update_power()
                self.update_status(self.pacman.score, self.pacman.lives,
                                 self.timer // 10)

                if self.timer % DIFFICULTY_SETTINGS[self.game_mode]["ghost_speed"] == 0:
                    for ghost in self.ghosts:
                        ghost.move(self.pacman.x, self.pacman.y,
                                  self.pacman.state == "powered")

                for ghost in self.ghosts:
                    if ghost.x == self.pacman.x and ghost.y == self.pacman.y:
                        if (self.pacman.state == 'powered'
                                and self.pacman.eat_ghost()):
                            ghost.respawn()
                        else:
                            self.pacman.lives -= 1
                            self.pacman.x, self.pacman.y = self.pacman.maze.pacman_start
                            self.pacman.update_position()
                            for g in self.ghosts:
                                g.respawn()
                            self.status_writer.goto(0, -260)
                            self.status_writer.write(
                                "Life lost!", 
                                align="center",
                                font=("Arial", 16, "bold"))
                            time.sleep(0.7)
                            self.status_writer.clear()

                if self.check_win_condition() or self.pacman.lives <= 0:
                    running = False
                    if self.check_win_condition():
                        self.game_over_screen(win=True)
                    else:
                        self.game_over_screen(win=False)

                    self.stats_manager.record_data(
                        self.pacman, self.timer // 10, self.game_mode)
                    self.stats_manager.save_to_file()
                    print(self.stats_manager.generate_report())

                    screen.onkeypress(lambda: self.restart(screen), "r")
                    screen.listen()

            except turtle.Terminator:
                break

    def restart(self, screen):
        """Restart the game with current settings"""
        screen.clear()
        screen.bgcolor("black")
        screen.tracer(0)
        self.__init__()
        self.start_game(self.game_mode)
        self.setup_controls(screen)
        self.run_game_loop(screen)


def choose_main_menu(screen, game_controller):
    """Display and handle main menu interactions"""
    button_drawer = turtle.Turtle()
    button_drawer.hideturtle()
    button_drawer.penup()
    button_drawer.color("white")

    button_drawer.goto(0, 160)
    button_drawer.write("Pixel Chomp", align="center", font=("Arial", 28, "bold"))

    menu_buttons = [("Play", 0, 80), ("Stats", 0, 40), ("Quit", 0, 0)]

    for label, x, y in menu_buttons:
        button_drawer.goto(x - 60, y - 15)
        button_drawer.begin_fill()
        button_drawer.fillcolor("gray")
        for _ in range(2):
            button_drawer.forward(120)
            button_drawer.left(90)
            button_drawer.forward(30)
            button_drawer.left(90)
        button_drawer.end_fill()
        button_drawer.goto(x, y - 10)
        button_drawer.write(label.upper(), align="center", font=("Arial", 16, "bold"))

    def check_click(x, y):
        """Handle menu button clicks"""
        for label, bx, by in menu_buttons:
            if bx - 60 < x < bx + 60 and by - 15 < y < by + 15:
                screen.onclick(None)
                button_drawer.clear()

                if label == "Play":
                    choose_difficulty(screen, game_controller)
                elif label == "Stats":
                    report = game_controller.stats_manager.generate_report()
                    print(report)
                    screen.bye()
                elif label == "Quit":
                    turtle.bye()

    screen.onclick(check_click)


def choose_difficulty(screen, game_controller):
    """Display and handle difficulty selection menu"""
    button_drawer = turtle.Turtle()
    button_drawer.hideturtle()
    button_drawer.penup()
    button_drawer.color("white")

    button_drawer.goto(0, 160)
    button_drawer.write("Choose Difficulty", align="center", font=("Arial", 24, "bold"))

    difficulties = ["easy", "normal", "hard"]
    positions = [(0, 80), (0, 40), (0, 0)]

    for i, level in enumerate(difficulties):
        x, y = positions[i]
        button_drawer.goto(x - 60, y - 15)
        button_drawer.begin_fill()
        button_drawer.fillcolor("gray")
        for _ in range(2):
            button_drawer.forward(120)
            button_drawer.left(90)
            button_drawer.forward(30)
            button_drawer.left(90)
        button_drawer.end_fill()
        button_drawer.goto(x, y - 10)
        button_drawer.write(level.upper(), align="center", font=("Arial", 16, "bold"))

    button_drawer.goto(-60, -75)
    button_drawer.begin_fill()
    button_drawer.fillcolor("gray")
    for _ in range(2):
        button_drawer.forward(120)
        button_drawer.left(90)
        button_drawer.forward(30)
        button_drawer.left(90)
    button_drawer.end_fill()
    button_drawer.goto(0, -70)
    button_drawer.write("BACK", align="center", font=("Arial", 16, "bold"))

    def check_click(x, y):
        """Handle difficulty selection clicks"""
        for i, level in enumerate(difficulties):
            bx, by = positions[i]
            if bx - 60 < x < bx + 60 and by - 15 < y < by + 15:
                screen.onclick(None)
                button_drawer.clear()
                screen.clear()
                screen.bgcolor("black")
                screen.tracer(0)
                game_controller.start_game(level)
                game_controller.setup_controls(screen)
                game_controller.run_game_loop(screen)

        if -60 < x < 60 and -75 < y < -45:
            screen.onclick(None)
            button_drawer.clear()
            screen.clear()
            screen.bgcolor("black")
            screen.tracer(0)
            choose_main_menu(screen, game_controller)

    screen.onclick(check_click)


def main():
    """Initialize and run the game"""
    screen = turtle.Screen()
    screen.bgcolor("black")
    canvas = screen.getcanvas()
    canvas.config(bg='black')
    screen.setup(width=600, height=600)
    screen.title("Pixel Chomp")
    screen.tracer(0)

    controller = GameController()
    choose_main_menu(screen, controller)

    screen.mainloop()


if __name__ == "__main__":
    main()
