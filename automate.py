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
import os

DELAY = 3600  # Seconds between posts
HASHTAGS = "#Chess #ChessGame #ChessBoard #ChessPlayer #ChessMaster #ChessTournament #ChessPost #ChessMemes " \
           "#Grandmaster #ChessLife #PlayingChess #BoardGames #Puzzle #ChessTactics #ChessPuzzle #ChessPuzzles"

########################################################################################################################
# Logging into instagram session
########################################################################################################################
USERNAME = "chessaccount3"
PASSWORD = input("Enter Password: ")
CURR_SESSION = "session.json"

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

####################################################################################################################
# Posting Puzzles
####################################################################################################################
puzzle_gen.load_puzzles()
while True:
    puzzle_gen.delete_slides()
    puzzle_gen.generate_slides()
    caption = 'White to play and win!\n'
    slides = []
    for file in os.listdir('Slides'):
        slides.append('Slides/' + file)
    cl.album_upload(slides, caption)

    # Append the puzzle ID we just posted into the repeats list
    with open('repeats.csv', mode="a", newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(puzzle_gen.puzzle)

    time.sleep(DELAY)
