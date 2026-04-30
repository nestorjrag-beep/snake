import curses
import random
import time
from collections import deque

WIDTH = 40
HEIGHT = 20

UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)

KEY_MAP = {
    curses.KEY_UP: UP,
    curses.KEY_DOWN: DOWN,
    curses.KEY_LEFT: LEFT,
    curses.KEY_RIGHT: RIGHT,
    ord("w"): UP,
    ord("s"): DOWN,
    ord("a"): LEFT,
    ord("d"): RIGHT,
}

OPPOSITES = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


def place_food(snake: deque) -> tuple[int, int]:
    snake_set = set(snake)
    while True:
        pos = (random.randint(1, HEIGHT - 2), random.randint(1, WIDTH - 2))
        if pos not in snake_set:
            return pos


def draw(win: curses.window, snake: deque, food: tuple, score: int) -> None:
    win.erase()
    win.border()
    win.addstr(0, 2, f" Score: {score} ")

    fy, fx = food
    win.addch(fy, fx, "@", curses.color_pair(2))

    for i, (y, x) in enumerate(snake):
        ch = "O" if i == 0 else "o"
        win.addch(y, x, ch, curses.color_pair(1))

    win.refresh()


def game_loop(win: curses.window) -> int:
    curses.curs_set(0)
    win.nodelay(True)
    win.keypad(True)

    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    snake: deque = deque([(HEIGHT // 2, WIDTH // 2)])
    direction = RIGHT
    food = place_food(snake)
    score = 0
    speed = 0.12

    while True:
        key = win.getch()
        if key == ord("q"):
            return score
        new_dir = KEY_MAP.get(key)
        if new_dir and new_dir != OPPOSITES.get(direction):
            direction = new_dir

        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        # wall collision
        if not (1 <= head[0] < HEIGHT - 1 and 1 <= head[1] < WIDTH - 1):
            return score

        # self collision
        if head in snake:
            return score

        snake.appendleft(head)

        if head == food:
            score += 10
            food = place_food(snake)
            speed = max(0.05, speed - 0.002)
        else:
            snake.pop()

        draw(win, snake, food, score)
        time.sleep(speed)


def main(stdscr: curses.window) -> None:
    curses.start_color()
    curses.use_default_colors()

    while True:
        rows, cols = stdscr.getmaxyx()
        if rows < HEIGHT or cols < WIDTH:
            stdscr.clear()
            stdscr.addstr(0, 0, f"Terminal too small. Need {WIDTH}x{HEIGHT}. Press q to quit.")
            stdscr.refresh()
            if stdscr.getch() == ord("q"):
                return
            continue

        win = curses.newwin(HEIGHT, WIDTH, (rows - HEIGHT) // 2, (cols - WIDTH) // 2)
        score = game_loop(win)

        stdscr.clear()
        msg = f"Game Over! Score: {score}"
        replay = "Play again? (y / q)"
        stdscr.addstr(rows // 2 - 1, (cols - len(msg)) // 2, msg)
        stdscr.addstr(rows // 2 + 1, (cols - len(replay)) // 2, replay)
        stdscr.refresh()

        while True:
            key = stdscr.getch()
            if key == ord("y"):
                break
            if key == ord("q"):
                return


if __name__ == "__main__":
    curses.wrapper(main)
