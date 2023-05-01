########################################################################################################################
# Used for testing the puzzle generator functionality. Does not deal with Instagrapi
# Rewrites insta_post.jpg each time ran.
########################################################################################################################
import csv
import random
from PIL import Image
import chess

########################################################################################################################
# Loading the puzzles from the database and choosing one and random
########################################################################################################################
puzzles = []
PUZZLES_LEN = 100000  # Number of puzzles to choose from
filename = "lichess_db_puzzle.csv"

with open(filename, 'r') as data:
    print("loading puzzles")
    for line in csv.reader(data):
        if len(puzzles) >= PUZZLES_LEN:
            break
        puzzles.append(line)
    print(PUZZLES_LEN, "puzzles loaded")

randNum = random.randint(0, PUZZLES_LEN - 1)
randPuzzle = puzzles[randNum]
fen = randPuzzle[1]
print(randPuzzle)
board = chess.Board(fen)
next_move = randPuzzle[2][0:4]
board.push_uci(next_move)
fen = board.fen()  # Updating fen to account for the blunder
whites_move = 'w' in fen

####################################################################################################################
# Creating the board image
####################################################################################################################
img_size = 1000  # resolution of the image
board_img = Image.open("Boards/chess_board_white_perspective.png").convert("RGBA")
if not whites_move:
    board_img = Image.open("Boards/chess_board_black_perspective.png").convert("RGBA")
piece_image = Image.open("Images/blackKing.png").convert("RGBA")
square_size = img_size // 8
border_size = 5
piece_size = square_size - 2 * border_size
piece_image = piece_image.resize((square_size, square_size))

images = {
    'p': "Images/blackPawn.png", 'r': "Images/blackRook.png", 'k': "Images/blackKing.png",
    'q': "Images/blackQueen.png", 'b': "Images/blackBishop.png", 'n': "Images/blackKnight.png",
    'P': "Images/whitePawn.png", 'R': "Images/whiteRook.png", 'K': "Images/whiteKing.png",
    'Q': "Images/whiteQueen.png", 'B': "Images/whiteBishop.png", 'N': "Images/whiteKnight.png"
}

cur_x = cur_y = 0
for char in fen:
    if char in images.keys():
        piece_img = Image.open(images[char]).convert("RGBA").resize((square_size, square_size))
        piece_pos = (square_size * cur_x, square_size * cur_y)
        if not whites_move:
            piece_pos = (square_size * (7 - cur_x), square_size * (7 - cur_y))
        board_img.alpha_composite(piece_img, dest=piece_pos)
        cur_x += 1
    elif char == '/':
        cur_x = 0
        cur_y += 1
    elif char == ' ':
        break
    else:
        cur_x += int(char)

board_img = board_img.convert('RGB')
board_img.save('insta_post.jpg')