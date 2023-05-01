########################################################################################################################
# Randomly chooses a puzzle from the Lichess puzzles database
# Creates an image of the puzzle and posts it to Instagram
########################################################################################################################
from instagrapi import Client
import csv
import random
from PIL import Image
import chess
import time
from instagrapi.exceptions import LoginRequired
import logging


DELAY = 300  # Seconds between posts
HASHTAGS = "#Chess #ChessGame #ChessBoard #ChessPlayer #ChessMaster #ChessTournament #ChessPost #ChessMemes " \
           "#Grandmaster #ChessLife #PlayingChess #BoardGames #Puzzle #ChessTactics #ChessPuzzle #ChessPuzzles"

########################################################################################################################
# Logging into instagram session
########################################################################################################################
USERNAME = "chesstesting"
PASSWORD = "hackme"
CURR_SESSION = "chesstesting.json"

logger = logging.getLogger()
cl = Client()
session = cl.load_settings(CURR_SESSION)
login_via_session = False
login_via_pw = False

if session:
    try:
        cl.set_settings(session)
        cl.login(USERNAME, PASSWORD)
        # check if session is valid
        try:
            cl.get_timeline_feed()
        except LoginRequired:
            logger.info("Session is invalid, need to login via username and password")
            old_session = cl.get_settings()
            # use the same device uuids across logins
            cl.set_settings({})
            cl.set_uuids(old_session["uuids"])
            cl.login(USERNAME, PASSWORD)
        login_via_session = True
    except Exception as e:
        logger.info("Couldn't login user using session information: %s" % e)

if not login_via_session:
    try:
        logger.info("Attempting to login via username and password. username: %s" % USERNAME)
        if cl.login(USERNAME, PASSWORD):
            login_via_pw = True
    except Exception as e:
        logger.info("Couldn't login user using username and password: %s" % e)

if not login_via_pw and not login_via_session:
    raise Exception("Couldn't login user with either password or session")

########################################################################################################################
# Loading the puzzles from the database and choosing one and random
########################################################################################################################
puzzles = []
PUZZLES_LEN = 3000000  # Number of puzzles to choose from
filename = "lichess_db_puzzle.csv"

with open(filename, 'r') as data:
    print("loading puzzles")
    for line in csv.reader(data):
        if len(puzzles) >= PUZZLES_LEN:
            break
        puzzles.append(line)
    print(PUZZLES_LEN, "puzzles loaded")

while True:
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

    ####################################################################################################################
    # Posting the puzzle
    ####################################################################################################################
    caption = 'White to play and win!\n'
    if not whites_move:
        caption = 'Black to play and win!\n'
    caption += 'Comment the solution once you find it!\n\n' + HASHTAGS
    cl.photo_upload("insta_post.jpg", caption)
    print("Puzzle posted to instagram")

    time.sleep(DELAY)
