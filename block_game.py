from numpy import block
import pygame
import random
import time
WIDTH = 720
HEIGHT = 1024
TPS = 100
GAME_SPEED = 60/TPS

# time
time_last_update = time.time()
time_accumulator = 0
time_slice = 1/TPS

# Define Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# initialize pygame and create window
pygame.init()
pygame.mixer.init()  # For sound
screen = pygame.Surface((WIDTH, HEIGHT))
output = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Game")
clock = pygame.time.Clock()  # For syncing the FPS


block_size = 100
TALLNESS = 50

# sprites
#background_sprite = pygame.transform.scale(pygame.image.load("background.jpg").convert(), (500,1000))
cube_sprite = pygame.transform.scale(pygame.image.load(
    "isometric_cube.png").convert_alpha(), (block_size, block_size))

START_RECT = pygame.Rect(60, 920, 165, 55)


class Block():
    def __init__(self, x, y, height, width, length, direction, colour=WHITE):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.length = length
        self.dir = direction
        self.colour = colour

        self.velocity = 4 * GAME_SPEED

        self.vel_x = 0
        self.vel_y = 0

        if direction:
            self.vel_x = self.velocity
        else:
            self.vel_y = self.velocity

        self.update_rect()

    def update_rect(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.length)

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.update_rect()

    def calc(self, cor, high=False):
        scale_x = 1
        scale_y = 0.5
        offset_y = -50
        height = self.height/2
        if high:
            height -= TALLNESS
        return [(self.x + cor[0] - self.y - cor[1])*scale_x + BLOCK_OFFSET[0],
                (self.y + cor[1] + self.x + cor[0])*scale_y + BLOCK_OFFSET[1] - height]

    def render(self, screen, scroll):
        pygame.draw.rect(screen, self.colour, self.rect)
        # scale_x = 0.5
        # scale_y = 0.25
        # offset_y = -50
        # height = -self.height/2
        # screen.blit(cube_sprite, (200+(self.x - self.y)*scale_x +
        #            BLOCK_OFFSET[0], (self.y + self.x)*scale_y + offset_y + height + BLOCK_OFFSET[1]))

        diag = (self.width**2 + self.length**2)**(1/2)
        pygame.draw.polygon(screen, BLUE, [self.calc((0, 0)), self.calc(
            (self.length, 0)), self.calc((self.length, self.width)), self.calc((0, self.width))])
        pygame.draw.polygon(screen, RED, [self.calc((0, 0), True), self.calc((self.length, 0), True), self.calc(
            (self.length, self.width), True), self.calc((0, self.width), True)])
        pygame.draw.polygon(screen, WHITE, [self.calc((0, self.width)), self.calc(
            (self.length, self.width)), self.calc((self.length, self.width), True), self.calc((0, self.width), True)])
        pygame.draw.polygon(screen, BLACK, [
            self.calc((self.length, 0)), self.calc((self.length, self.width)), self.calc((self.length, self.width), True), self.calc((self.length, 0), True)])
        #print(self.calc((0, 0)))


SCROLL = (0, 0)
BLOCK_OFFSET = (0, 0)


def render():
    global main_block
    screen.fill(GREEN)
    for block in immovable_blocks:
        block.render(screen, SCROLL)
    main_block.render(screen, SCROLL)
    output.blit(screen, (0, 0))


def update(splice):
    main_block.update()


def randcol():
    return [random.randint(0, 255) for i in range(3)]


direction = False

START_DIST = 500
def generate_block():
    global main_block, direction
    xpos = immovable_blocks[-1].x
    ypos = immovable_blocks[-1].y
    if direction:
        main_block = Block(
            xpos-START_DIST, ypos, immovable_blocks[-1].height + block_size, immovable_blocks[-1].width, immovable_blocks[-1].length, direction, colour=randcol())
    else:
        main_block = Block(
            xpos, ypos-START_DIST, immovable_blocks[-1].height + block_size, immovable_blocks[-1].width, immovable_blocks[-1].length, direction, colour=randcol())
    direction = not direction


def press():
    if not main_block.rect.colliderect(immovable_blocks[-1]):
        lose()
    else:
        print("yay")

    main_block.width-= abs(main_block.y - immovable_blocks[-1].y)
    main_block.length-= abs(main_block.x - immovable_blocks[-1].x)

    main_block.x = max(immovable_blocks[-1].x, main_block.x)
    main_block.y = max(immovable_blocks[-1].y, main_block.y)

    immovable_blocks.append(main_block)
    generate_block()


def lose():
    print("LOST")
    sys.exit()
    input()

    restart()


BLOCK_OFFSET = (0, -200)
# Game Variables
immovable_blocks = [
    Block(HEIGHT+40, WIDTH, 0, block_size+100, block_size+100, True)]
main_block = Block(HEIGHT-START_DIST, WIDTH, block_size, block_size+100, block_size+100, True)

print(immovable_blocks[0].calc((0, 0)))

# Game loop
running = True
start_game = False
keyed_up = True


def main():
    global running, time_last_update, time_accumulator, time_slice, start_game, keyed_up
    while running:
        # gets all the events which have occured till now and keeps tab of them.
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if START_RECT.collidepoint(event.pos):
                    start_game = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and keyed_up:
                    start_game = True
                    keyed_up = False

                    press()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    keyed_up = True

        delta_time = time.time() - time_last_update
        time_last_update += delta_time
        time_accumulator += delta_time

        while time_accumulator > time_slice:
            # print(time_accumulator)
            update(1)
            time_accumulator -= time_slice

        render()  # 3 Draw/render
        pygame.display.flip()  # Done after drawing everything to the screen

    # end of main loop


if __name__ == '__main__':
    main()

pygame.quit()
