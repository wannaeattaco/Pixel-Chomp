# Pac-Man Game using Turtle and OOP with Power Pellets and File-based Maze Loading
import turtle
import random
import time
import csv

TILE_SIZE = 24
POWER_DURATION = 5000  # milliseconds

class Maze:
    def __init__(self, filename):
        self.layout = []
        self.walls = []
        self.dots = []
        self.power_pellets = []
        self.load_from_file(filename)

    def load_from_file(self, filename):
        with open(filename, newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                self.layout.append([int(cell) for cell in row])

    def load_maze(self):
        drawer = turtle.Turtle()
        drawer.penup()
        drawer.speed(0)
        drawer.hideturtle()

        for y, row in enumerate(self.layout):
            for x, cell in enumerate(row):
                screen_x = -len(row) * TILE_SIZE // 2 + x * TILE_SIZE
                screen_y = len(self.layout) * TILE_SIZE // 2 - y * TILE_SIZE

                if cell == 0:
                    drawer.goto(screen_x, screen_y)
                    drawer.color("black")
                    drawer.begin_fill()
                    for _ in range(4):
                        drawer.forward(TILE_SIZE)
                        drawer.right(90)
                    drawer.end_fill()
                elif cell == 1:
                    dot = turtle.Turtle()
                    dot.shape("circle")
                    dot.color("white")
                    dot.penup()
                    dot.speed(0)
                    dot.shapesize(0.2, 0.2)
                    dot.goto(screen_x + TILE_SIZE // 2, screen_y - TILE_SIZE // 2)
                    self.dots.append(dot)
                elif cell == 2:
                    pellet = turtle.Turtle()
                    pellet.shape("circle")
                    pellet.color("blue")
                    pellet.penup()
                    pellet.speed(0)
                    pellet.shapesize(0.4, 0.4)
                    pellet.goto(screen_x + TILE_SIZE // 2, screen_y - TILE_SIZE // 2)
                    self.power_pellets.append(pellet)
                elif cell in (3, 4, 9):
                    drawer.goto(screen_x, screen_y)
                    drawer.color("blue")
                    drawer.setheading(0 if cell in (4, 9) else -90)
                    drawer.pendown()
                    drawer.forward(TILE_SIZE)
                    drawer.penup()
                    self.walls.append((screen_x + TILE_SIZE // 2, screen_y - TILE_SIZE // 2))

    def check_collision(self, x, y):
        return (x, y) in self.walls

    def remove_dot(self, pac):
        for dot in self.dots:
            if pac.sprite.distance(dot) < 15:
                dot.goto(1000, 1000)
                self.dots.remove(dot)
                return 10
        return 0

    def check_power_pellet(self, pac):
        for pellet in self.power_pellets:
            if pac.sprite.distance(pellet) < 15:
                pellet.goto(1000, 1000)
                self.power_pellets.remove(pellet)
                return True
        return False

class PacMan:
    def __init__(self, maze):
        self.sprite = turtle.Turtle()
        self.sprite.shape("circle")
        self.sprite.color("yellow")
        self.sprite.penup()
        self.sprite.speed(0)
        self.sprite.goto(-200, 200)
        self.speed = TILE_SIZE
        self.state = "normal"
        self.lives = 3
        self.maze = maze
        self.power_timer = None

    def move(self, dx, dy):
        new_x = self.sprite.xcor() + dx
        new_y = self.sprite.ycor() + dy
        if not self.maze.check_collision(new_x, new_y):
            self.sprite.goto(new_x, new_y)

    def eat_dot(self):
        return self.maze.remove_dot(self)

    def check_power(self):
        if self.maze.check_power_pellet(self):
            self.power_up()

    def power_up(self):
        self.state = "powered"
        if self.power_timer:
            turtle.ontimer(None, self.power_timer)
        self.power_timer = turtle.ontimer(self.reset_power, POWER_DURATION)

    def reset_power(self):
        self.state = "normal"

    def eat_ghost(self):
        if self.state == "powered":
            return 200
        return 0

class Ghost:
    def __init__(self, x, y, color, maze):
        self.sprite = turtle.Turtle()
        self.sprite.shape("circle")
        self.sprite.color(color)
        self.sprite.penup()
        self.sprite.speed(0)
        self.sprite.goto(x, y)
        self.speed = TILE_SIZE
        self.maze = maze

    def move(self):
        dx, dy = random.choice([(TILE_SIZE, 0), (-TILE_SIZE, 0), (0, TILE_SIZE), (0, -TILE_SIZE)])
        new_x = self.sprite.xcor() + dx
        new_y = self.sprite.ycor() + dy
        if not self.maze.check_collision(new_x, new_y):
            self.sprite.goto(new_x, new_y)

    def check_collision(self, pacman):
        return self.sprite.distance(pacman.sprite) < 20

class GameController:
    def __init__(self, filename):
        self.maze = Maze(filename)
        self.maze.load_maze()
        self.pacman = PacMan(self.maze)
        self.ghosts = [Ghost(-120, 120, color, self.maze) for color in ("red", "pink", "cyan")]
        self.score = 0

        self.pen = turtle.Turtle()
        self.pen.color("white")
        self.pen.penup()
        self.pen.hideturtle()
        self.pen.goto(-200, 260)
        self.update_score()

        screen = turtle.Screen()
        screen.listen()
        screen.onkey(lambda: self.pacman.move(-TILE_SIZE, 0), "Left")
        screen.onkey(lambda: self.pacman.move(TILE_SIZE, 0), "Right")
        screen.onkey(lambda: self.pacman.move(0, TILE_SIZE), "Up")
        screen.onkey(lambda: self.pacman.move(0, -TILE_SIZE), "Down")

        self.screen = screen

    def update_score(self):
        self.pen.clear()
        self.pen.write(f"Score: {self.score} Lives: {self.pacman.lives}", align="left")

    def update(self):
        self.score += self.pacman.eat_dot()
        self.pacman.check_power()

        for ghost in self.ghosts:
            ghost.move()
            if ghost.check_collision(self.pacman):
                if self.pacman.state == "powered":
                    self.score += self.pacman.eat_ghost()
                    ghost.sprite.goto(-120, 120)
                else:
                    self.pacman.lives -= 1
                    self.update_score()
                    if self.pacman.lives <= 0:
                        self.pen.goto(-50, 0)
                        self.pen.write("Game Over")
                        return

        self.update_score()
        self.screen.update()
        if not self.maze.dots:
            self.pen.goto(-50, 0)
            self.pen.write("You Win!")
        else:
            self.screen.ontimer(self.update, 400)

    def start(self):
        self.update()

# Start game with external maze file (e.g. "maze.csv")
game = GameController("maze.csv")
game.start()
turtle.mainloop()
