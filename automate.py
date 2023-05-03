########################################################################################################################
# Randomly chooses a puzzle from the Lichess puzzles database
# Creates an image of the puzzle and posts it to Instagram
########################################################################################################################
import csv
from instagrapi import Client
import time
from instagrapi.exceptions import LoginRequired
import logging
import puzzle_gen

DELAY = 3600  # Seconds between posts
HASHTAGS = "#Chess #ChessGame #ChessBoard #ChessPlayer #ChessMaster #ChessTournament #ChessPost #ChessMemes " \
           "#Grandmaster #ChessLife #PlayingChess #BoardGames #Puzzle #ChessTactics #ChessPuzzle #ChessPuzzles"
cl = Client()

########################################################################################################################
# Logging into instagram session
########################################################################################################################
USERNAME = "chessaccount3"
CURR_SESSION = "session.json"
no_login = True # For testing purposes, skip the login and upload process
exit_loop = True  # For testing purposes, run once rather than continuously

if not no_login:
    PASSWORD = input("Enter Password: ")
    logger = logging.getLogger()
    print("Logging into instagram...")
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
    print("Login complete.")

####################################################################################################################
# Posting Puzzles
####################################################################################################################
puzzle_gen.load_puzzles()
while True:
    puzzle_gen.generate_slides()
    queued_puzzle = puzzle_gen.puzzle

    caption = 'White to play '
    if 'w' in queued_puzzle[1]:  # Lichess starts the puzzle a move early.
        caption = 'Black to play '
    theme = queued_puzzle[7]
    if 'mate' in theme:
        caption += 'and checkmate their opponent!\n'
    else:
        caption += 'and win!\n'
    caption += '\n' + HASHTAGS

    num_moves = len(queued_puzzle[2].split(" "))  # Number of moves in the puzzle
    slides = []
    # Slides will always have 10 jpgs (0 - 9). Only the updated IMGs get uploaded. The rest will contain garbage
    for f in range(0, num_moves):
        slides.append('Slides/slide' + str(f))

    if not no_login:
        cl.album_upload(slides, caption)
        print("Puzzle uploaded to instagram")

    # Append the puzzle ID we just posted into the repeats list
    with open('repeats.csv', mode="a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(puzzle_gen.puzzle)

    if exit_loop:
        break;
    time.sleep(DELAY)
