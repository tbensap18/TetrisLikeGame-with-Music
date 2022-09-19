import pygame
import random

pygame.mixer.init()
pygame.font.init()

# GLOBALS VARS
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 20 height per block
block_size = 30

## Represents top left position of play area, thats when start drawing blocks and
## check for collisions
top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

# SHAPE FORMATS
# Represents the shapes in the game, multidimensional lists for each shape for rotations
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
# color of shapes S=
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]


# index 0-6 represent shape

# Main data structure of our game. Class represents different pieces which can be called in the functions
# Holds information of x, y, width, height for the pieces.
class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


def create_grid(locked_pos={}):
    # Create 1 list for every row in grid. Since we have 20 rows,
    # we create 20 sublists and each sublist have 10 colors, as we have 10 squares in each row
    grid = [[(0, 0, 0) for x in range(10)] for x in range(20)]

    #
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                c = locked_pos[(j, i)]
                grid[i][j] = c

    return grid


# Converts the shapes given in lists for computer to understand
def convert_shape_format(shape):
    positions = []  # For generating list of positions
    # Whenever passing a shape, it will have a list full of lists, but to pick acutal sublist we should get shape
    # rotation modulus the length of the shape
    format = shape.shape[shape.rotation % len(shape.shape)]

    # loop through shape to look at every row and column of the lists to check if 0 exists, if exists, it will add
    # position into list.
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    # Fix offsetting by taking every x value added and subtract 2 from it
    # and every y value and subtract 4 from it. Will move everything to LEFT and UP
    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


# See if block is moved to a valid space
def valid_space(shape, grid):
    # Takes all positions in list and adding it to one dimensional list or flattens the list making it alot easier to loop through
    # E.g: [[(0,1)],[(2,3)]] -> [(0,1), (2,3)]
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in
                    range(20)]  # Adds position to accepted position if empty
    accepted_pos = [j for sub in accepted_pos for j in sub]

    formatted = convert_shape_format(shape)

    # Check if the position exists within accepted positions
    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True


# Checks if any of the positions are above screen, So if hits y value 0, We know we are above screen so game loses.
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True

    return False


# function to randomly select shapes from the shapes list
def get_shape():
    return Piece(5, 0, random.choice(shapes))


# Function for the ingame texts which appears at start and end of the game.
def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont("freesansbold", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (
        top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + play_height / 2 - label.get_height()))


# Draws the line for the grid
def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    for i in range(len(grid)):
        pygame.draw.line(surface, (128, 128, 128), (sx, sy + i * block_size), (sx + play_width, sy + i * block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (sx + j * block_size, sy),
                             (sx + j * block_size, sy + play_height))


# This function clears the rows once every row is filled with colored blocks.
def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid) - 1, -1,
                   -1):  # Loops through grid backwards, So it starts at 20th row and its going to move up to 19th row
        row = grid[i]  # Sets row to every row in grid
        if (0, 0, 0) not in row:  # If color (0,0,0) is not in row
            inc += 1  # For every deleted row, we add 1 increment
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue

    # Shifts every row above deleted row moves down by 1.
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:  # For every key in our sorted list of locked
            # positions based on the y value looking at it backwards hence the [::-1] e.g [(0,1),(0,0)] -> [(0,0),(0,
            # 1)]
            x, y = key  # Key is a tuple
            if y < ind:  # Shifts rows down after deleting rows
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(
                    key)  # Creates new key in locked positions which is same colored value as last key

    return inc


# Function that draws the font and next shape in the User Interface
def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('freesansbold', 30)
    label = font.render('Next Shape', 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color,
                                 (sx + j * block_size, sy + i * block_size, block_size, block_size), 0)

    # draw label on screen
    surface.blit(label, (sx + 10, sy - 30))


# Function that updates the score into the text file.
def update_score(nscore):
    score = max_score()

    with open('scores.txt', 'w') as f:
        if int(score) > nscore:
            f.write(str(score))
        else:
            f.write(str(nscore))


# Function that checks and updates score from text file.
def max_score():
    with open('scores.txt', 'r') as f:
        lines = f.readlines()
        score = lines[0].strip()

    return score


# Function that draws the window or User Interface of the game.
def draw_window(surface, grid, score=0, last_score=0):
    surface.fill((0, 0, 0))

    pygame.font.init()
    font = pygame.font.SysFont('freesansbold', 60)
    label = font.render('Our Column Game', 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    # Current Score
    font = pygame.font.SysFont('freesansbold', 30)
    label = font.render('Score: ' + str(score), 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100

    surface.blit(label, (sx + 20, sy + 160))

    # Last Score
    label = font.render('High Score: ' + last_score, 1, (255, 255, 255))

    sx = top_left_x - 200
    sy = top_left_y + 200

    surface.blit(label, (sx + 20, sy + 160))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            # (surface to draw on, color, position in which its being drawn, width, height, fill)
            pygame.draw.rect(surface, grid[i][j],
                             (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)

    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)

    draw_grid(surface, grid)


# Function in which the game variables are stored and functions are called and run.
def main(win):
    last_score = max_score()
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    level_time = 0
    score = 0

    while run:
        grid = create_grid(
            locked_positions)  # To constantly update the grid so that when were drawing it to the screen we get an
        # updated version
        fall_time += clock.get_rawtime()  # Tracks amount of time since last clock.tick() function
        level_time += clock.get_rawtime()
        clock.tick()

        # Adds piece falling faster for every 5 seconds
        if level_time / 1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005

        # Makes pieces move down the screen
        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        # Breaks while loop when run = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Checks what specific key is being hit, and codes what each key does
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1  # current_piece = get_shape() which returns random shapes. Starts at 0.
                    if not (valid_space(current_piece, grid)):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.rotation -= 1

        shape_pos = convert_shape_format(current_piece)
        # Add colors to pieces in the grid.
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:  # Means not above the screen
                grid[y][x] = current_piece.color

        # Happens when block hits bottom or freezes
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10  # Whenever we clear row we add 10 to the score.

        draw_window(win, grid, score, last_score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        # Checks if we lost the Game or Not
        if check_lost(locked_positions):
            draw_text_middle(win, "LOSER! HEHE", 80, (255, 255, 255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            update_score(score)
            pygame.mixer.music.stop()


# Function for the main menu of the game.
def main_menu(win):
    run = True
    while run:
        pygame.mixer.music.load('columngame.mid')
        pygame.mixer.music.play(-1, 0.0)
        win.fill((255, 255, 255))
        draw_text_middle(win, "Press a Key To Play", 60, (0, 0, 0))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()

            if event.type == pygame.KEYDOWN:
                main(win)

    pygame.display.quit()


# For running program
win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Our Column Game')
main_menu(win)
