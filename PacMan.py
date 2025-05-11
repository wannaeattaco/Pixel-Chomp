"""PacMan class"""
import turtle


class PacMan:
    """Represents the player with movement and state management"""
    TILE_SIZE = 24
    START_LIVES = 3
    DOT_SCORE = 10
    POWER_SCORE = 50
    GHOST_SCORE = 200
    DOT_SIZE = 10
    POWER_SIZE = 16
    MAZE_OFFSET_X = -252
    MAZE_OFFSET_Y = 252
    NORMAL_STATE = 'normal'
    POWERED_STATE = 'powered'

    def __init__(self, maze, settings):
        """Initialize Pac-Man"""
        self.maze = maze
        self.settings = settings
        self.x, self.y = maze.pacman_start
        self.state = self.NORMAL_STATE
        self.power_timer = 0
        self.lives = self.START_LIVES
        self.score = 0
        self.dots_collected = 0
        self.ghosts_eaten = 0
        self.power_pallets_collected = 0
        self._setup_icon()

    def _setup_icon(self):
        """Setup Pac-Man's turtle icon"""
        self.icon = turtle.Turtle()
        self.icon.shape('circle')
        self.icon.color('yellow')
        self.icon.penup()
        self.icon.speed(0)
        self.update_position()
        self.icon.showturtle()

    def _calculate_screen_position(self, x, y):
        """Calculate screen coordinates from grid position"""
        sx = self.MAZE_OFFSET_X + (x * self.TILE_SIZE) + self.TILE_SIZE / 2
        sy = self.MAZE_OFFSET_Y - (y * self.TILE_SIZE) - self.TILE_SIZE / 2
        return sx, sy

    def power_up(self):
        """Activate power up effects"""
        self.state = self.POWERED_STATE
        self.power_timer = self.settings["power_duration"]

    def change_state(self):
        """Update power pellet timer and state"""
        if self.state == self.POWERED_STATE:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.state = self.NORMAL_STATE

    def move(self, dx, dy, drawer=None):
        """Move Pac-Man in given direction if possible"""
        nx, ny = self.x + dx, self.y + dy
        if not self.maze.check_collision(nx, ny):
            val = self.maze.layout[ny][nx]
            if val == 1:
                self.score += self.DOT_SCORE
                self.dots_collected += 1
                self.maze.layout[ny][nx] = 3
            elif val == 2:
                self.score += self.POWER_SCORE
                self.power_pallets_collected += 1
                self.maze.layout[ny][nx] = 3
                self.power_up()
            if drawer:
                sx, sy = self._calculate_screen_position(nx, ny)
                drawer.goto(sx, sy)
                drawer.dot(self.POWER_SIZE if val == 2 else self.DOT_SIZE, 'black')
            self.x, self.y = nx, ny
            self.update_position()

    def update_position(self):
        """Update Pac-Man's position on screen"""
        sx, sy = self._calculate_screen_position(self.x, self.y)
        self.icon.goto(sx, sy)
        self.icon.showturtle()

    def eat_ghost(self):
        """Eat a ghost when powered up"""
        if self.state == self.POWERED_STATE:
            self.ghosts_eaten += 1
            self.score += self.GHOST_SCORE
            return True
        return False
