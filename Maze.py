"""Maze class"""
from maze_layout import LAYOUTS


class Maze:
    """Represents the game maze with walls and items"""
    TILE_SIZE = 24
    MAZE_OFFSET_X = -252
    MAZE_OFFSET_Y = 252

    def __init__(self, difficulty="easy"):
        """Initialize maze with difficulty level"""
        self.layout = LAYOUTS[difficulty]
        self.pacman_start = self._find_pacman_start()
        self.ghost_spawns = self._find_ghost_spawns()

    def _find_pacman_start(self):
        """Find Pac-Man's starting position"""
        for y, row in enumerate(self.layout):
            for x, cell in enumerate(row):
                if cell == 4:
                    return x, y
        return 0, 0

    def _find_ghost_spawns(self):
        """Find ghost spawn positions"""
        spawns = []
        for y, row in enumerate(self.layout):
            for x, cell in enumerate(row):
                if cell == 5:
                    spawns.append((x, y))
        return spawns

    def check_collision(self, x, y):
        """Check if position is a wall"""
        return self.layout[y][x] == 0

    def load_maze(self, drawer):
        """Load and draw maze on screen"""
        drawer.clear()
        drawer.penup()
        drawer.speed(0)
        drawer.hideturtle()

        for y, row in enumerate(self.layout):
            for x, cell in enumerate(row):
                screen_x = self.MAZE_OFFSET_X + (x * self.TILE_SIZE)
                screen_y = self.MAZE_OFFSET_Y - (y * self.TILE_SIZE)

                if cell == 0:
                    drawer.goto(screen_x, screen_y)
                    drawer.color('blue')
                    drawer.begin_fill()
                    for _ in range(4):
                        drawer.forward(self.TILE_SIZE)
                        drawer.right(90)
                    drawer.end_fill()
                elif cell == 1:
                    drawer.goto(screen_x + self.TILE_SIZE/2, screen_y - self.TILE_SIZE/2)
                    drawer.color('white')
                    drawer.dot(8)
                elif cell == 2:
                    drawer.goto(screen_x + self.TILE_SIZE/2, screen_y - self.TILE_SIZE/2)
                    drawer.color('white')
                    drawer.dot(14)
