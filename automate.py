########################################################################################################################
# Randomly chooses a puzzle from the Lichess puzzles database
# Creates an image of the puzzle and posts it to Instagram
########################################################################################################################
import csv
from instagrapi import Client, exceptions
from datetime import datetime
import time
import pytz
import logging
import puzzle_gen

USERNAME = "chesscrunch"
PASSWORD = "64Chessify!"
CURR_SESSION = "session.json"
cl = Client()
cl.delay_range = [1, 3]
POST_TIMES = ['8', '09', '12', '16']

HASHTAGS = "#Chess #ChessGame #ChessBoard #ChessPlayer #ChessMaster #ChessTournament #ChessPost #ChessMemes " \
           "#Grandmaster #ChessLife #PlayingChess #BoardGames #Puzzle #ChessTactics #ChessPuzzle #ChessPuzzles"


########################################################################################################################
# Logging into instagram session
########################################################################################################################
def insta_log():
    global PASSWORD
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
            except exceptions.LoginRequired:
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
def run_bot():
    insta_log()
    puzzle_gen.load_puzzles()
    while True:
        # First, make sure that we are allowed to post during this hour.
        current_time = datetime.now()
        current_time_zone = current_time.astimezone(pytz.timezone('America/New_York'))
        formatted_time = current_time_zone.strftime('%Y-%m-%d %H:%M:%S %Z%z')
        clock_time = formatted_time.split(" ")[1].split(":")  # [Hour, Minutes, Seconds]
        hour = clock_time[0]  # The current hour as a string
        can_post = False
        for t in POST_TIMES:
            if hour == t:
                can_post = True
        if not can_post:
            continue  # Skip posting until it is time

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

        num_moves = len(queued_puzzle[2].split(" "))  # Number of moves in the puzzle
        slides = []
        # Slides will always have 10 jpgs (0 - 9). Only the updated IMGs get uploaded. The rest will contain garbage
        for f in range(0, num_moves):
            slides.append('Slides/Slide' + str(f) + '.jpg')

        try:
            cl.album_upload(slides, caption)
            print("Puzzle uploaded to instagram")
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

        except Exception as e:
            print("Failed to upload: ", e)
            if "Please wait a few minutes" in str(e):
                print("Instagram requests we wait a few minutes. Will try again tomorrow :(")
                time.sleep(86400)  # Wait one day
                continue
            else:
                print("Instagram terminated our session. Will try again tomorrow :(")
                insta_log()
                time.sleep(86400)
                continue

        time.sleep(3600)  # Check again in an hour


run_bot()
