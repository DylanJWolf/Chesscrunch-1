########################################################################################################################
# Used for testing the puzzle generation aspect of the bot
# Creates new slides each time it is ran
########################################################################################################################
import csv
import puzzle_gen

POST_TIMES = ['8', '12', '16']

HASHTAGS = "#Chess #ChessGame #ChessBoard #ChessPlayer #ChessMaster #ChessTournament #ChessPost #ChessMemes " \
           "#Grandmaster #ChessLife #PlayingChess #BoardGames #Puzzle #ChessTactics #ChessPuzzle #ChessPuzzles"

####################################################################################################################
# Posting Puzzles
####################################################################################################################
puzzle_gen.load_puzzles()
puzzle_gen.generate_slides()
queued_puzzle = puzzle_gen.puzzle

# Generating caption
caption = 'White to play'
if 'w' in queued_puzzle[1]:  # Lichess starts the puzzle a move early.
    caption = 'Black to play'
theme = queued_puzzle[7]
if 'mate' in theme:
    puzzle_theme = queued_puzzle[7]
    mateInX = puzzle_theme.find("mateIn") + 6  # Sting index to the number of moves
    caption += ", checkmate in " + str(puzzle_theme[mateInX]) + " moves!"
else:
    caption += ' and win!'
if int(queued_puzzle[3]) > 2600:
    caption += ' If you can solve this, you are a master.'
elif int(queued_puzzle[3]) > 2550:
    caption += ' This is a difficult one.'
caption += '\nToo tough for you? Swipe for the solution.\nFollow us for daily puzzles!\n\n' + HASHTAGS
print("Caption:\n" + caption)

num_moves = len(queued_puzzle[2].split(" "))  # Number of moves in the puzzle
slides = []
# Slides will always have 10 jpgs (0 - 9). Only the updated IMGs get uploaded. The rest will contain garbage
for f in range(0, num_moves):
    slides.append('Slides/Slide' + str(f) + '.jpg')

puzzle_gen.puzzle_index += 1

# Append the puzzle ID we just posted into the repeats list
with open('repeats.csv', mode="a", newline='') as file:
    writer = csv.writer(file)
    writer.writerow(puzzle_gen.puzzle)

# Once we've reached the end of the puzzles database, just restart and clear repeats.csv
if puzzle_gen.puzzle_index == puzzle_gen.PUZZLES_LEN:
    puzzle_gen.puzzle_index = 0
    f = open('repeats.csv', mode="w+")
    f.close()
    puzzle_gen.repeats.clear()

# Increment the theme index and piece index so the next post is different
with open('Themes/theme_index.txt', mode="r") as file:
    theme_index = (int(file.read()) + 1) % len(puzzle_gen.themes)
with open('Themes/theme_index.txt', mode="w") as file:
    file.write(str(theme_index))

# Only increment the piece index once per theme cycle
if theme_index == 0:
    with open('Pieces/piece_index.txt', mode="r") as file:
        piece_index = (int(file.read()) + 1) % len(puzzle_gen.piece_sets)
    with open('Pieces/piece_index.txt', mode="w") as file:
        file.write(str(piece_index))