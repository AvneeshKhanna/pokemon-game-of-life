import pygame
import numpy as np
from scipy import signal

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1280
SQUARE_SIDE = 40

ALIVE_COLOR_ONE = 'red'
ALIVE_ONE_VALUE = 11.0

ALIVE_COLOR_TWO = 'yellow'
ALIVE_TWO_VALUE = 3.0

DEAD_COLOR = 'black'
DEAD_VALUE = 0

# load Pokémon images and rescale
ONE_IMG = pygame.image.load("resources/charmander-square.jpg")
ONE_IMG = pygame.transform.scale(ONE_IMG, (SQUARE_SIDE, SQUARE_SIDE))
TWO_IMG = pygame.image.load("resources/bulbasaur-square.jpg")
TWO_IMG = pygame.transform.scale(TWO_IMG, (SQUARE_SIDE, SQUARE_SIDE))

CELL_MATRIX = np.zeros((SCREEN_HEIGHT // SQUARE_SIDE, SCREEN_WIDTH // SQUARE_SIDE))


def draw_grid(screen):
    global SCREEN_HEIGHT, SCREEN_WIDTH, SQUARE_SIDE

    pos = pygame.Vector2(0, 0)
    for x in range(SCREEN_WIDTH // SQUARE_SIDE):
        pos.y = 0
        for y in range(SCREEN_HEIGHT // SQUARE_SIDE):

            # randomly generate seed cells. 'p' controls the probability of cell state
            p = 0.25
            n = [1, 1]
            cell_states = np.random.binomial(n, p)
            if cell_states[0] == 1 and cell_states[1] == 0:
                CELL_MATRIX[y, x] = ALIVE_ONE_VALUE
                block_color = ALIVE_COLOR_ONE
                img = ONE_IMG

                screen.blit(img, (pos.x, pos.y))
            elif cell_states[0] == 0 and cell_states[1] == 1:
                CELL_MATRIX[y, x] = ALIVE_TWO_VALUE
                block_color = ALIVE_COLOR_TWO
                img = TWO_IMG

                screen.blit(img, (pos.x, pos.y))
            else:
                CELL_MATRIX[y, x] = DEAD_VALUE
                block_color = DEAD_COLOR

                # print(f"Cell coloured at x={pos.x} y={pos.y}")
                rect = pygame.Rect(pos.x, pos.y, SQUARE_SIDE, SQUARE_SIDE)
                pygame.draw.rect(screen, block_color, rect)

            pos.y += SQUARE_SIDE

        pos.x += SQUARE_SIDE


def produce_next_generation():
    """
    Next generation is produced according to the following rules:

    1. Any live cell with two or three live neighbours survives.
    2. Any dead cell with three live neighbours becomes a live cell taking the colour of the majority no. of neighbours
    3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.
    :return:
    """
    global CELL_MATRIX

    neighbour_counter = np.array([
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1]
    ])
    moore_neighbours = signal.convolve2d(CELL_MATRIX, neighbour_counter, boundary='fill', mode='same')

    next_gen_map = np.zeros_like(CELL_MATRIX)

    # rule set A: 2 or 3 alive neighbours
    next_gen_map[(moore_neighbours == 2*ALIVE_ONE_VALUE)     # 2*11
                 | (moore_neighbours == 2*ALIVE_TWO_VALUE)    # 2*3
                 | (moore_neighbours == ALIVE_ONE_VALUE + ALIVE_TWO_VALUE)   # 11+3
                 | (moore_neighbours == ALIVE_ONE_VALUE + 2*ALIVE_TWO_VALUE)   # 2*3 + 11
                 | (moore_neighbours == 2*ALIVE_ONE_VALUE + ALIVE_TWO_VALUE)   # 2*11 + 3
                 | (moore_neighbours == 3*ALIVE_TWO_VALUE)    # 3*3
                 | (moore_neighbours == 3*ALIVE_ONE_VALUE)   # 3*11
    ] = 1

    # retain cells based on rule set A
    CELL_MATRIX = CELL_MATRIX * next_gen_map

    # rule set B: 3 alive neighbours with both colours
    # change cells based on rule set B
    CELL_MATRIX[(moore_neighbours == ALIVE_ONE_VALUE + 2*ALIVE_TWO_VALUE) & (CELL_MATRIX == DEAD_VALUE)] = ALIVE_TWO_VALUE
    CELL_MATRIX[(moore_neighbours == 3*ALIVE_TWO_VALUE) & (CELL_MATRIX == DEAD_VALUE)] = ALIVE_TWO_VALUE
    CELL_MATRIX[(moore_neighbours == 2*ALIVE_ONE_VALUE + ALIVE_TWO_VALUE) & (CELL_MATRIX == DEAD_VALUE)] = ALIVE_ONE_VALUE
    CELL_MATRIX[(moore_neighbours == 3*ALIVE_ONE_VALUE) & (CELL_MATRIX == DEAD_VALUE)] = ALIVE_ONE_VALUE


def update_grid(screen):
    global DEAD_COLOR, ALIVE_COLOR_ONE, CELL_MATRIX, SQUARE_SIDE

    # clear previous screen
    screen.fill(DEAD_COLOR)

    # retrieve alive cell updated locations
    alive_ys, alive_xs = np.where(CELL_MATRIX != DEAD_VALUE)

    # mark new alive cells
    for alive_y, alive_x in zip(alive_ys, alive_xs):

        if CELL_MATRIX[alive_y, alive_x] == ALIVE_TWO_VALUE:
            cell_colour = ALIVE_COLOR_TWO
            img = TWO_IMG
        else:
            cell_colour = ALIVE_COLOR_ONE
            img = ONE_IMG

        # print(f"Alive cell found at y={alive_y * SQUARE_SIDE}, x={alive_x * SQUARE_SIDE}")
        # rect = pygame.Rect(alive_x * SQUARE_SIDE, alive_y * SQUARE_SIDE, SQUARE_SIDE, SQUARE_SIDE)
        # pygame.draw.rect(screen, cell_colour, rect)

        screen.blit(img, (alive_x * SQUARE_SIDE, alive_y * SQUARE_SIDE))


# def update_grid_user(screen, mouse_x, mouse_y):
#     global SQUARE_SIDE, ALIVE_COLOR_ONE, ALIVE_COLOR_TWO, CELL_MATRIX
#
#     if np.random.binomial(1, 0.5) == 1:
#         block_colour = ALIVE_COLOR_ONE
#         cell_value = ALIVE_ONE_VALUE
#     else:
#         block_colour = ALIVE_COLOR_TWO
#         cell_value = ALIVE_TWO_VALUE
#
#     # snap to grid
#     snap_pos_x = mouse_x // SQUARE_SIDE
#     snap_pos_y = mouse_y // SQUARE_SIDE
#
#     # update cell matrix
#     impact_radius = 6  # denoting the number of blocks to make alive
#     CELL_MATRIX[snap_pos_y:snap_pos_y + impact_radius, snap_pos_x:snap_pos_x + impact_radius] = cell_value
#
#     # update block color
#     rect = pygame.Rect(snap_pos_x * SQUARE_SIDE, snap_pos_y * SQUARE_SIDE, SQUARE_SIDE * impact_radius,
#                        SQUARE_SIDE * impact_radius)
#     pygame.draw.rect(screen, block_colour, rect)


def main():
    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    dt = 0

    mouse_active = False
    start = False
    period = 20
    iteration = 1

    # draw an empty grid on screen
    draw_grid(screen)

    while True:
        # poll for events
        for event in pygame.event.get():

            # pygame.QUIT event means the user clicked 'X' to close your window
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # toggle mouse input when mouse button is pressed
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_active = not mouse_active
                start = True

            # draw on screen based on user mouse movement
            # if mouse_active and event.type == pygame.MOUSEMOTION:
            #     mouse_x, mouse_y = pygame.mouse.get_pos()
            #     update_grid_user(screen, mouse_x, mouse_y)

        if iteration % period == 0 and start:
            print(f"iteration is {iteration}")
            # produce next generation cells
            produce_next_generation()
            # update screen with the next generation cells
            update_grid(screen)
            # reset iteration
            iteration = 0

        # flip() the display to put your work on screen
        pygame.display.flip()

        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        dt = clock.tick(60) / 1000
        # print(dt)

        iteration += 1


if __name__ == '__main__':
    main()
