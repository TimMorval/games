import pygame
import sys
import random


class Block:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Food:
    def __init__(self):
        x = random.randint(0, NB_COL - 1)
        y = random.randint(0, NB_ROW - 1)
        self.block = Block(x, y)

    def draw_food(self):
        rect = pygame.Rect(self.block.x * CELL_SIZE, self.block.y *
                           CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, (72, 212, 98), rect)


class Snake:
    def __init__(self):
        self.body = [Block(2, 6), Block(3, 6), Block(4, 6)]
        self.direction = "RIGHT"

    def draw_snake(self):
        for block in self.body:
            x_pos = block.x * CELL_SIZE
            y_pos = block.y * CELL_SIZE
            rect = pygame.Rect(x_pos, y_pos, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (83, 177, 253), rect)

    def move_snake(self):
        old_head = self.body[-1]
        if self.direction == "RIGHT":
            new_head = Block(old_head.x + 1, old_head.y)
        elif self.direction == "LEFT":
            new_head = Block(old_head.x - 1, old_head.y)
        elif self.direction == "TOP":
            new_head = Block(old_head.x, old_head.y - 1)
        elif self.direction == "DOWN":
            new_head = Block(old_head.x, old_head.y + 1)
        self.body.append(new_head)


class Game:
    def __init__(self):
        self.food = Food()
        self.snake = Snake()
        self.generate_food()

    def update(self):
        self.snake.move_snake()
        self.check_head_on_food()
        self.game_over()

    def draw_game_element(self):
        self.food.draw_food()
        self.snake.draw_snake()

    def check_head_on_food(self):
        snake_head = self.snake.body[-1]
        food = self.food.block
        if snake_head.x == food.x and snake_head.y == food.y:
            self.generate_food()
        else:
            self.snake.body.pop(0)

    def generate_food(self):
        while True:
            is_on_snake = False
            for block in self.snake.body:
                if block.x == self.food.block.x and block.y == self.food.block.y:
                    is_on_snake = True
                    self.food = Food()
                    break
            if not is_on_snake:
                break

    def game_over(self):
        snake_head = self.snake.body[-1]
        if snake_head.x not in range(NB_COL) or snake_head.y not in range(NB_ROW):
            self.snake = Snake()
        for block in self.snake.body[:-1]:
            if block.x == snake_head.x and block.y == snake_head.y:
                self.snake = Snake()
                break


pygame.init()

NB_COL = 10
NB_ROW = 15
CELL_SIZE = 40

screen = pygame.display.set_mode((NB_COL * CELL_SIZE, NB_ROW * CELL_SIZE))
timer = pygame.time.Clock()

SCREEN_UPDATE = pygame.USEREVENT
pygame.time.set_timer(SCREEN_UPDATE, 200)


def show_grid():
    for i in range(NB_COL):
        for j in range(NB_ROW):
            rect = pygame.Rect(i * CELL_SIZE, j * CELL_SIZE,
                               CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, pygame.Color("black"), rect, 1)


game = Game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == SCREEN_UPDATE:
            game.update()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if game.snake.direction != "DOWN":
                    game.snake.direction = "TOP"
            if event.key == pygame.K_DOWN:
                if game.snake.direction != "TOP":
                    game.snake.direction = "DOWN"
            if event.key == pygame.K_LEFT:
                if game.snake.direction != "RIGHT":
                    game.snake.direction = "LEFT"
            if event.key == pygame.K_RIGHT:
                if game.snake.direction != "LEFT":
                    game.snake.direction = "RIGHT"
    screen.fill(pygame.Color("white"))
    show_grid()
    game.draw_game_element()
    pygame.display.update()
    timer.tick(60)  # 60 frames per second
