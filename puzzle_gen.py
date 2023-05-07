########################################################################################################################
# Used for testing the puzzle generator functionality. Does not deal with Instagrapi
########################################################################################################################
import csv
from PIL import Image
import chess

########################################################################################################################
# Loading the puzzles from the database
########################################################################################################################
puzzles = []
repeats = []  # List of puzzles that we have already posted
themes = ['Themes/Purple/', 'Themes/Blue/', 'Themes/Green/']  # List of themes I've got.
piece_sets = ['Pieces/cardinal/', 'Pieces/cburnett/', 'Pieces/maestro/']  # List of piece sets I've got.
PUZZLES_LEN = 2394  # Number of puzzles to choose from
puzzle_index = 0  # Current position in the puzzle database
piece_index = 0  # Current piece set to use
puzzle = None  # Puzzle currently being made
filename = "puzzles_database.csv"


def load_puzzles():
    # Load puzzle database into puzzles
    with open(filename, 'r') as data:
        print("loading puzzles...")
        for line in csv.reader(data):
            if len(puzzles) >= PUZZLES_LEN:
                break
            puzzles.append(line)
        print(PUZZLES_LEN, "puzzles loaded")

    # Load puzzles we've posted already into repeats
    # We only need to do this when the script is restarted. The puzzle index increments on its own
    with open('repeats.csv') as file:
        for line in csv.reader(file):
            repeats.append(line)


def generate_slides():
    global puzzle_index, piece_index, puzzle
    puzzle = puzzles[puzzle_index]
    # If we have posted this puzzle, increment puzzle index until we find one we haven't posted
    while puzzle in repeats:
        puzzle = puzzles[puzzle_index]
        puzzle_index += 1
    fen = puzzle[1]
    moves = puzzle[2].split(" ")
    print("Queuing puzzle:", puzzle)

    ####################################################################################################################
    # Creating the board images
    ####################################################################################################################
    with open('Themes/theme_index.txt', mode="r") as file:
        theme = themes[int(file.read())]
    with open('Pieces/piece_index.txt', mode="r") as file:
        piece_set = piece_sets[int(file.read())]

    whites_move = 'w' not in puzzle[1]  # Lichess starts the puzzles a move early
    board = chess.Board(fen)

    for m in range(len(moves)):
        move = moves[m]
        board.push_uci(moves[m])
        fen = board.fen()  # Updating board state for previous move

        board_img = Image.open(theme + "whitePerspective.png").convert("RGBA")
        if not whites_move:
            board_img = Image.open(theme + "blackPerspective.png").convert("RGBA")
        last_move = Image.open(theme + "lastMove.png").convert("RGBA")

        pieces = {
            'p': piece_set + "blackPawn.png", 'r': piece_set + "blackRook.png", 'k': piece_set + "blackKing.png",
            'q': piece_set + "blackQueen.png", 'b': piece_set + "blackBishop.png", 'n': piece_set + "blackKnight.png",
            'P': piece_set + "whitePawn.png", 'R': piece_set + "whiteRook.png", 'K': piece_set + "whiteKing.png",
            'Q': piece_set + "whiteQueen.png", 'B': piece_set + "whiteBishop.png", 'N': piece_set + "whiteKnight.png"
        }

        img_size = 1000  # resolution of the image
        square_size = img_size // 8

        # Calculating position of highlighted squares to indicate next more
        last_square_x = last_square_y = new_square_x = new_square_y = 0
        if whites_move:
            last_square_x = (ord(move[0]) - ord('a')) * square_size
            last_square_y = (8 - int(move[1])) * square_size
            new_square_x = (ord(move[2]) - ord('a')) * square_size
            new_square_y = (8 - int(move[3])) * square_size
        else:
            last_square_x = (7 - (ord(move[0]) - ord('a'))) * square_size
            last_square_y = (int(move[1]) - 1) * square_size
            new_square_x = (7 - (ord(move[2]) - ord('a'))) * square_size
            new_square_y = (int(move[3]) - 1) * square_size

        if m != 0:
            board_img.paste(last_move, (last_square_x, last_square_y), last_move)
            board_img.paste(last_move, (new_square_x, new_square_y), last_move)

        # Reading the FEN and placing the pieces onto the board
        cur_x = cur_y = 0
        for char in fen:
            if char in pieces.keys():
                piece_img = Image.open(pieces[char]).convert("RGBA").resize((square_size, square_size))
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
        img_path = 'Slides/slide' + str(m) + ".jpg"
        board_img.save(img_path)
