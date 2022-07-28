import pygame
from pygame.locals import *
import sys
import random
import copy
 
# 定数 
MAX_ROW = 20
MAX_COL = 20

class Block:
    def __init__(self, block_type):
        self.shapes = [[], [], # empty block and wall
                  [[0, -1], [0, 0], [0, 1], [0, 2]], # I block
                  [[-1, -1], [0, -1], [0, 0], [0, 1]], # J block
                  [[0, -1], [0, 0], [0, 1], [-1, 1]], # L block
                  [[0, -1], [0, 0], [-1, 0], [-1, 1]], # S blosk
                  [[-1, -1], [-1, 0], [0, 0], [0, 1]], # Z block
                  [[0, -1], [0, 0], [-1, 0], [0, 1]], # T block
                  [[0, 0], [-1, 0], [0, 1], [-1, 1]]] # square

        self.block_type = block_type
        self.shape = copy.deepcopy(self.shapes[block_type])
        self.row = 1 # initial position
        self.col = 5
        self.level = 0
        self.drop_rate = [60, 50, 45, 42, 39, 36, 35, 34, 33, 32, 31,
                          30, 29, 28, 27, 26, 25, 24, 23, 22, 21,
                          20, 19, 18, 17, 16, 15, 14, 13, 12, 11,
                          10,  9,  8,  7,  6,  5,  4,  3,  2,  1, 0]
        self.count = 60
        self.hold_flag = True

    # key command movement
    def move(self, board, direction): # direction down:0 left:1 right:2 bottom:3
        if direction == 0 and self.moveable(board, [1, 0]):
            self.row += 1
        elif direction == 1 and self.moveable(board, [0, -1]):
            self.col -= 1
        elif direction == 2 and self.moveable(board, [0, 1]):
            self.col +=1
        elif direction == 3:
            self.row += self.bottom(board)
            self.count = 60

    def bottom(self, board): #
        direction = [1, 0]
        while self.moveable(board, direction):
            direction[0] += 1
        return direction[0]-1

    def rotate(self, board, direction): # clockwise:0 anticloskwise:1
        # long bar rotates differently
        if self.block_type == 2:
            if direction == 0:
                for dx in self.shape:
                    dx[0], dx[1] = dx[1], 1-dx[0]
            elif direction == 1:
                for dx in self.shape:
                    dx[0], dx[1] = 1-dx[1], dx[0]


        # square doesn`t rotate
        elif self.block_type == 8:
            pass

        # other blocks
        elif direction == 0:
            for dx in self.shape:
                dx[0], dx[1] = dx[1], -dx[0]
        elif direction == 1:
            for dx in self.shape:
                dx[0], dx[1] = -dx[1], dx[0]

        self.rotate_correction(board)

    # moving downward due to time
    def drop(self, screen, board):
        if self.count < self.drop_rate[self.level]:
            self.count += 1
            return 0
        elif self.moveable(board, [1, 0]):
            self.count = 0
            self.row += 1
            return 0
        else:
            return 1 # make new block

    def moveable(self, board, direction):
        drow, dcol = direction

        for dx in self.shape:
            row = self.row + dx[0] + drow
            col = self.col + dx[1] + dcol
            if 0 <= row < MAX_ROW + 3 and 0 <= col < MAX_COL + 2 and board[row][col] != 0:
                return False

        return True

    def rotate_correction(self, board):
        move_priority = [[0, 0], [0, -1], [0, 1], [-1, 0], [1, 0], [2, 0], [-1, 1], [1, 1]]
        for direction in move_priority:
            if self.moveable(board, direction):
                self.row += direction[0]
                self.col += direction[1]
                return

        direction = [0, 2]
        while not self.moveable(board, direction):
            direction[1] += 1
        self.row += direction[0]
        self.col += direction[1]

    def draw(self, screen, block_color, board):
        # prediction when dropped
        drow = self.bottom(board)
        for row, col in self.shape:
            row += self.row + drow
            col += self.col
            if row > 1:
                pygame.draw.rect(screen, block_color[self.block_type], Rect(30+35*col, 50+35*(row-2), 35, 35))
                pygame.draw.rect(screen, block_color[10], Rect(32+35*col, 52+35*(row-2), 31, 31))

        for row, col in self.shape:
            row += self.row
            col += self.col
            if row > 1:
                pygame.draw.rect(screen, (0, 0, 0), Rect(30+35*col, 50+35*(row-2), 35, 35))
                pygame.draw.rect(screen, block_color[self.block_type], Rect(32+35*col, 52+35*(row-2), 31, 31))

    def place(self, screen, board, record):
        for dx in self.shape:
            row = self.row + dx[0]
            col = self.col + dx[1]
            if not (2 <= row < MAX_ROW+2 and 1 <= col < MAX_COL+1): # placed block outside screen
                gameover(screen, record)
                return 1

            board[row][col] = self.block_type
        return 0

class Record:
    def __init__(self):
        self.cleared_row = 0
        self.score = 0
        self.level = 0
        self.score_table = [0, 80, 100, 300, 1200]
        self.level_up = [2, 5, 8, 12, 16, 20, 25, 30, 35, 40, # level 0 to 9
                         46, 52, 58, 64, 70, 77, 84, 91, 98, 105, # level 10 to 19
                         112, 120, 128, 136, 144, 152, 160, 168, 177, 186, # level 20 to 29
                         195, 204, 213, 222, 231, 240, 255, 270, 285, 300, 1000] # 30 to 40

    def update(self, count):
        self.score += self.score_table[count]*(self.level+1)
        self.cleared_row += count

        if self.level < 40 and self.level_up[self.level] <= self.cleared_row: # level 40 is max
            self.level += 1

    def show(self, screen):
        font = pygame.font.Font(None, 50)
        text1 = font.render("LEVEL:", True, (255, 255, 255))
        level = font.render("{}".format(self.level), True, (255, 255, 255))
        screen.blit(text1, [850, 300])
        screen.blit(level, [1000, 300])

        text2 = font.render("CLEARED ROW:", True, (255, 255, 255))
        cleared_row = font.render("{}".format(self.cleared_row), True, (255, 255, 255))
        screen.blit(text2, [850, 360])
        screen.blit(cleared_row, [1200, 360])

        text3 = font.render("SCORE", True, (255, 255, 255))
        score = font.render("{0:012d}".format(self.score), True, (255, 255, 255))
        screen.blit(text3, [850, 420])
        screen.blit(score, [1000, 480])

def start(screen):
    font1 = pygame.font.Font(None, 150)
    title = font1.render("TETRIS", True, (255, 255, 255))
    font2 = pygame.font.Font(None, 50)
    text = font2.render("Press ENTER to start", True, (255, 255, 255))

    screen.blit(title, [200, 100])
    screen.blit(text, [200, 300])

    pygame.draw.rect(screen, (255, 255, 255), Rect(600, 250, 450, 450), 3)
    pygame.draw.rect(screen, (0, 0, 0), Rect(700, 330, 310, 40))

    font1 = pygame.font.Font(None, 80)
    text1 = font1.render("COMMAND", True, (255, 255, 255))
    screen.blit(text1, [650, 275])
    font3 = pygame.font.Font(None, 40)
    text2 = font3.render("Arrow DOWN: Move down", True, (255, 255, 255))
    screen.blit(text2, [640, 350])
    text2 = font3.render("Arrow LEFT: Move left", True, (255, 255, 255))
    screen.blit(text2, [640, 390])
    text2 = font3.render("Arrow RIGHT: Move right", True, (255, 255, 255))
    screen.blit(text2, [640, 430])
    text2 = font3.render("Arrow UP: Move bottom", True, (255, 255, 255))
    screen.blit(text2, [640, 470])
    text2 = font3.render("D:  Rotate anticlockwise", True, (255, 255, 255))
    screen.blit(text2, [640, 510])
    text2 = font3.render("A:  Rotate clockwise", True, (255, 255, 255))
    screen.blit(text2, [640, 550])
    text2 = font3.render("H:  Hold", True, (255, 255, 255))
    screen.blit(text2, [640, 590])
    text2 = font3.render("P:  Pause", True, (255, 255, 255))
    screen.blit(text2, [640, 630])

    pygame.display.update()

    while(1):
        pygame.time.wait(50)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == K_RETURN:
                    return

# 記録の初期化
def initialize_game():
    board = [[0 for i in range(MAX_COL+2)] for j in range(MAX_ROW+3)]
    for col in range(MAX_COL+2):
        board[-1][col] = 1
    for row in range(MAX_ROW+3):
        board[row][0] = 1
        board[row][-1] = 1

    record = Record()

    block_type = random.randint(2, 8)
    block = Block(block_type)
    block.level = record.level
    block_type = random.randint(2, 8)
    next_block = Block(block_type)

    hold_block = None

    return board, record, block, next_block, hold_block

# 出力　消える行数、消える行の番号
def find_deleting_row(board):
    count = 0
    row_numbers = []
    for row in range(2, MAX_ROW+2):
        flag = True
        for col in range(1, MAX_COL+1):
            if board[row][col] == 0:
                flag = False
                break

        # row filled
        if flag:
            count += 1
            row_numbers.append(row)

    return count, row_numbers

# 行削除
def delete_row(screen, board, row_number, block_color):
    n_col = 4
    for row in row_number:
        for col in range(1, MAX_COL+1):
            board[row][col] = 0
    for i in range(n_col+MAX_COL):
        for row in row_number:
            for col in reversed(range(1, MAX_COL+1)):
                board[row][col] = board[row][col-1]
            if i < n_col:
                board[row][1] = 9
        pygame.time.wait(8)
        draw_board(screen, board, block_color)
        pygame.display.update()

    for deleting_row in row_number:
        for row in reversed(range(2, deleting_row+1)):
            for col in range(1, MAX_COL+1):
                board[row][col] = board[row-1][col]
# ゲームオーバー
def gameover(screen, record):
    screen.fill((0, 0, 0))
    font1 = pygame.font.Font(None, 200)
    gameover_text = font1.render("GAMEOVER", True, (255, 0, 0))
    screen.blit(gameover_text, [250, 100])

    font2 = pygame.font.Font(None, 80)
    result_text = font2.render("RESULT", True, (255, 255, 255))
    screen.blit(result_text, [350, 300])

    font = pygame.font.Font(None, 50)
    text1 = font.render("LEVEL:", True, (255, 255, 255))
    level = font.render("{}".format(record.level), True, (255, 255, 255))
    screen.blit(text1, [400, 370])
    screen.blit(level, [750, 370])

    text2 = font.render("CLEARED ROW:", True, (255, 255, 255))
    cleared_row = font.render("{}".format(record.cleared_row), True, (255, 255, 255))
    screen.blit(text2, [400, 430])
    screen.blit(cleared_row, [750, 430])

    text3 = font.render("SCORE", True, (255, 255, 255))
    score = font2.render("{0:012d}".format(record.score), True, (255, 255, 255))
    screen.blit(text3, [400, 490])
    screen.blit(score, [450, 550])

    restart_text = font.render("Press R to restart", True, (255, 255, 255))
    screen.blit(restart_text, [500, 650])

    pygame.display.update()

    while(1):
        pygame.time.wait(50)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == K_r:
                    return

def pause(screen, board, block_color):
    pygame.draw.rect(screen, (50, 50, 50), Rect(65, 51, 35*MAX_COL, 35*MAX_ROW))
    font1 = pygame.font.Font(None, 100)
    text1 = font1.render("PAUSE", True, (255, 255, 255))
    font2 = pygame.font.Font(None, 30)
    text2 = font2.render("Press P to resume", True, (255, 255, 255))
    text3 = font2.render("Press R to start new game", True, (255, 255, 255))
    screen.blit(text1, [300, 250])
    screen.blit(text2, [300, 350])
    screen.blit(text3, [300, 400])
    pygame.display.update()

    while(1):
        pygame.time.wait(50)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == K_p:
                    draw_board(screen, board, block_color)
                    pygame.display.update()
                    return 0

                # restart
                if event.key == K_r:
                    return 1

def hold(block, next_block, hold_block, record):
    # no block in hold
    if hold_block == None:
        block_type = random.randint(2, 8)
        new_block = Block(block_type)
        block, next_block, hold_block = next_block, new_block, block
        hold_block.hold_flag = False
        block.row = 1
        block.col = 5
        hold_block.shape = hold_block.shapes[hold_block.block_type]

    # first hold
    elif block.hold_flag:
        block, hold_block = hold_block, block
        hold_block.hold_flag = False
        block.row = 1
        block.col = 5
        hold_block.shape = hold_block.shapes[hold_block.block_type]

    block.level = record.level

    return block, next_block, hold_block

def draw_hold(screen, hold_block, block_color):
    pygame.draw.rect(screen, (255, 255, 255), Rect(1100, 30, 150, 150))
    pygame.draw.rect(screen, (0, 0, 0), Rect(1105, 35, 140, 140))
    pygame.draw.rect(screen, (0, 0, 0), Rect(1120, 30, 70, 10))
    font = pygame.font.Font(None, 30)
    text = font.render("HOLD", True, (255, 255, 255))
    screen.blit(text, [1130, 20])
    if hold_block != None:
        for dx in hold_block.shape:
            if hold_block.block_type == 2 or hold_block.block_type == 8:
                pygame.draw.rect(screen, (20, 20, 20), Rect(1150+25*dx[1], 105+25*dx[0], 25, 25))
                pygame.draw.rect(screen, block_color[hold_block.block_type], Rect(1152+25*dx[1], 107+25*dx[0], 21, 21))
            else:
                pygame.draw.rect(screen, (20, 20, 20), Rect(1162+25*dx[1], 105+25*dx[0], 25, 25))
                pygame.draw.rect(screen, block_color[hold_block.block_type], Rect(1164+25*dx[1], 107+25*dx[0], 21, 21))

def draw_next(screen, block, block_color):
    pygame.draw.rect(screen, (255, 255, 255), Rect(900, 30, 150, 150))
    pygame.draw.rect(screen, (0, 0, 0), Rect(905, 35, 140, 140))
    pygame.draw.rect(screen, (0, 0, 0), Rect(920, 30, 70, 10))
    font = pygame.font.Font(None, 30)
    text = font.render("NEXT", True, (255, 255, 255))
    screen.blit(text, [930, 20])
    for dx in block.shape:
        if block.block_type == 2 or block.block_type == 8:
            pygame.draw.rect(screen, (20, 20, 20), Rect(950+25*dx[1], 105+25*dx[0], 25, 25))
            pygame.draw.rect(screen, block_color[block.block_type], Rect(952+25*dx[1], 107+25*dx[0], 21, 21))
        else:
            pygame.draw.rect(screen, (20, 20, 20), Rect(962+25*dx[1], 105+25*dx[0], 25, 25))
            pygame.draw.rect(screen, block_color[block.block_type], Rect(964+25*dx[1], 107+25*dx[0], 21, 21))

# ゲームボード

#　スクリーン、ゲームボード、ブロックの色
def draw_board(screen, board, block_color):
    for row in range(2, MAX_ROW+3):
        for col in range(MAX_COL+2):
            pygame.draw.rect(screen, (0, 0, 0), Rect(30+35*col, 50+35*(row-2), 35, 35))
            if board[row][col] < 2:
                pygame.draw.rect(screen, block_color[board[row][col]], Rect(31+35*col, 51+35*(row-2), 34, 34))
            else:
                pygame.draw.rect(screen, block_color[board[row][col]], Rect(32+35*col, 52+35*(row-2), 31, 31))

def main():
    pygame.init()
    screen = pygame.display.set_mode((1300, 850))
    pygame.display.set_caption("Tetris") # title bar

    block_color = [(50, 50, 50), (150, 150, 150), (255, 0, 0), (0, 0, 255), (255, 165, 0),
                   (255, 0, 255), (0, 255, 0), (0, 255, 255), (255, 255, 0), (200, 200, 200), (100, 100, 100)]

    board, record, block, next_block, hold_block = initialize_game()

    start(screen)

    while(1):
        pygame.time.wait(10)

        screen.fill((0, 0, 0)) # fill with black R:0 G:0 B:0

        draw_board(screen, board, block_color)

        # move command
        pressed_key = pygame.key.get_pressed()
        if pressed_key[K_k]:
            block.move(board, 0)
        if pressed_key[K_j]:
            block.move(board, 1)
        if pressed_key[K_l]:
            block.move(board, 2)

        bottom_flag = block.drop(screen, board)
        block.draw(screen, block_color, board)
        record.show(screen)
        draw_next(screen, next_block, block_color)
        draw_hold(screen, hold_block, block_color)
        pygame.display.update()

        if bottom_flag == 1:
            gameover_flag = block.place(screen, board, record)
            if gameover_flag == 1:
                board, record, block, next_block, hold_block = initialize_game()

            else:
                count, row_numbers = find_deleting_row(board)
                if count > 0:
                    delete_row(screen, board, row_numbers, block_color)
                    record.update(count)

                block_type = random.randint(2, 8)
                while block_type == block.block_type and block_type == next_block.block_type:
                    block_type = random.randint(2, 8)

                block = next_block
                block.level = record.level
                if not block.moveable(board, [0, 0]): # new block unplaceable
                    gameover(screen, record)
                    board, record, block, next_block, hold_block = initialize_game() # if resume was selected

                next_block = Block(block_type)

        for event in pygame.event.get():
            # close button
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                # escape key pressed
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                # block rotetion
                if event.key == K_d : # anti-clockwise
                    block.rotate(board, 1)
                if event.key == K_a: # clockwise
                    block.rotate(board, 0)

                # block movement
                if event.key == K_DOWN:
                    block.move(board, 0)
                if event.key == K_LEFT:
                    block.move(board, 1)
                if event.key == K_RIGHT:
                    block.move(board, 2)

                if event.key == K_UP: # move to bottom
                    block.move(board, 3)

                # pause
                if event.key == K_p:
                    restart_flag = pause(screen, board, block_color)
                    if restart_flag == 1:
                        board, record, block, next_block, hold_block = initialize_game()

                # hold
                if  event.key == K_h:
                    block, next_block, hold_block = hold(block, next_block, hold_block, record)

if __name__ == "__main__":
    main()