"""Ghost class"""
import turtle
import heapq


class Ghost:
    """Represents a ghost with AI movement"""
    GHOST_COLORS = {
        'red': '#FF0000',
        'pink': '#FFB8FF',
        'cyan': '#00FFFF',
        'orange': '#FFB852'
    }

    @staticmethod
    def register_ghost_shape(color):
        """Register a custom ghost shape for the given color if not already registered."""
        shape_name = f"ghost_{color}"
        screen = turtle.Screen()
        if shape_name in screen.getshapes():
            return shape_name
        poly = (
            (9.0, -12.0), (-3.0, -12.0), (-7.5, -10.5), (-10.5, -7.5), (-12.0, -3.75),
            (-12.0, 0.0), (-12.0, 3.75), (-10.5, 7.5), (-7.5, 10.5), (-3.0, 12.0),
            (9.0, 12.0), (6.75, 9.75), (9.0, 7.5), (6.75, 5.25), (9.0, 3.0), (6.75, 0.75),
            (9.0, 0.0), (6.75, -0.75), (9.0, -3.0), (6.75, -5.25), (9.0, -7.5),
            (6.75, -9.75), (9.0, -12.0)
        )
        screen.register_shape(shape_name, poly)
        return shape_name

    def __init__(self, maze, color='red', spawn=None):
        """Initialize ghost with color and spawn point"""
        self.maze = maze
        self.start = spawn or maze.ghost_spawns[0]
        self.x, self.y = self.start
        self.original_color = color
        self.shape_name = Ghost.register_ghost_shape(color)
        self.icon = turtle.Turtle()
        self.icon.shape(self.shape_name)
        self.icon.color(self.GHOST_COLORS[self.original_color])
        self.icon.penup()
        self.icon.speed(0)
        self.animation_frame = 0
        self.animation_direction = 1
        self.update_position()

    def _register_ghost_shape(self):
        """Create custom ghost shape"""
        if self.shape_name not in turtle.getshapes():
            ghost = turtle.Turtle()
            ghost.hideturtle()
            ghost.penup()
            ghost.color(self.GHOST_COLORS[self.original_color])
            ghost.begin_fill()
            ghost.circle(10)
            ghost.end_fill()
            ghost.getscreen().register_shape(self.shape_name, ghost.get_shapepoly())

    def _setup_icon(self):
        """Setup ghost's turtle icon"""
        self.icon = turtle.Turtle()
        self.icon.shape(self.shape_name)
        self.icon.penup()
        self.icon.speed(0)
        self.update_position()

    def pathfinding(self, target_x, target_y, powered=False):
        """A* pathfinding algorithm to find path to target"""
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        def get_neighbors(pos):
            x, y = pos
            neighbors = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if not self.maze.check_collision(nx, ny):
                    neighbors.append((nx, ny))
            return neighbors

        start = (self.x, self.y)
        if powered:
            valid_positions = []
            for y in range(len(self.maze.layout)):
                for x in range(len(self.maze.layout[0])):
                    if not self.maze.check_collision(x, y):
                        valid_positions.append((x, y))

            max_distance = -1
            furthest_pos = None
            for pos in valid_positions:
                dist = heuristic(pos, (target_x, target_y))
                if dist > max_distance:
                    max_distance = dist
                    furthest_pos = pos

            goal = furthest_pos
        else:
            goal = (target_x, target_y)

        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            current = heapq.heappop(frontier)[1]
            if current == goal:
                break

            for next_pos in get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + heuristic(goal, next_pos)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current

        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from.get(current)
            if current is None:
                return []
        path.reverse()
        return path

    def move(self, tx, ty, powered):
        """Move ghost towards target position"""
        if powered:
            self.icon.color('blue')
        else:
            self.icon.color(self.GHOST_COLORS[self.original_color])

        path = self.pathfinding(tx, ty, powered)
        if path:
            next_x, next_y = path[0]
            self.x, self.y = next_x, next_y
            self.update_position()

    def update_position(self, powered=False, power_timer=None, power_duration=None):
        """Update ghost's position on screen"""
        TILE_SIZE = 24

        sx = -252 + (self.x * TILE_SIZE)
        sy = 252 - (self.y * TILE_SIZE)
        self.icon.goto(sx + TILE_SIZE // 2, sy - TILE_SIZE // 2)
        self.icon.shape(self.shape_name)
        if powered:
            if power_timer is not None and power_duration is not None and \
            power_timer < 0.2 * power_duration:
                if (power_timer // 2) % 2 == 0:
                    self.icon.color('#0000FF')
                else:
                    self.icon.color('white')
            else:
                self.icon.color('#0000FF')
        else:
            self.icon.color(self.GHOST_COLORS[self.original_color])
        self.icon.showturtle()

    def respawn(self):
        """Return ghost to spawn point"""
        self.x, self.y = self.start
        self.update_position()
