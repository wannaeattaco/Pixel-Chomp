"""Pixel Chomp"""
import turtle
from GameController import GameController


def main():
    """Set up the game"""
    status_writer = turtle.Turtle()
    status_writer.color("white")
    status_writer.penup()
    status_writer.hideturtle()
    status_writer.speed(0)

    controller = GameController(status_writer)
    controller.show_main_menu()


if __name__ == "__main__":
    main()
