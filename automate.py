########################################################################################################################
# Randomly chooses a puzzle from the Lichess puzzles database
# Creates an image of the puzzle and posts it to Instagram
########################################################################################################################
import csv
from instagrapi import Client
from instagrapi import exceptions
import time
import logging
import puzzle_gen

DELAY = 1200  # Seconds between posts
proxy1 = "http://lvzgfwlq:nu7g7fkk78hi@2.56.119.93:5074"
proxy2 = "http://lvzgfwlq:nu7g7fkk78hi@185.199.229.156:7492"
curr_proxy = proxy1
cl = Client()
cl.set_proxy(curr_proxy)

USERNAME = "chessaccount3"
CURR_SESSION = "session.json"
no_login = False  # For testing purposes, skip the login and upload process
exit_loop = False  # For testing purposes, run once rather than continuously

HASHTAGS = "#Chess #ChessGame #ChessBoard #ChessPlayer #ChessMaster #ChessTournament #ChessPost #ChessMemes " \
           "#Grandmaster #ChessLife #PlayingChess #BoardGames #Puzzle #ChessTactics #ChessPuzzle #ChessPuzzles"


# Swap proxies to evade IP bans
def switch_proxy():
    global curr_proxy
    if curr_proxy == proxy1:
        curr_proxy = proxy2
        cl.set_proxy(proxy2)
    else:
        curr_proxy = proxy1
        cl.set_proxy(proxy1)
    print("Proxy switched")


########################################################################################################################
# Logging into instagram session
########################################################################################################################
def insta_log():
    password = input("Enter Password: ")
    logger = logging.getLogger()
    print("Logging into instagram...")
    session = cl.load_settings(CURR_SESSION)
    login_via_session = False
    login_via_pw = False

    if session:
        try:
            cl.set_settings(session)
            cl.login(USERNAME, password)
            # check if session is valid
            try:
                cl.get_timeline_feed()
            except exceptions.LoginRequired:
                logger.info("Session is invalid, need to login via username and password")
                old_session = cl.get_settings()
                # use the same device uuids across logins
                cl.set_settings({})
                cl.set_uuids(old_session["uuids"])
                cl.login(USERNAME, password)
            login_via_session = True
        except Exception as e:
            logger.info("Couldn't login user using session information: %s" % e)

    if not login_via_session:
        try:
            logger.info("Attempting to login via username and password. username: %s" % USERNAME)
            if cl.login(USERNAME, password):
                login_via_pw = True
        except Exception as e:
            logger.info("Couldn't login user using username and password: %s" % e)

    if not login_via_pw and not login_via_session:
        raise Exception("Couldn't login user with either password or session")
    print("Login complete.")


if not no_login:
    insta_log()

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
        slides.append('Slides/slide' + str(f) + '.jpg')

    if not no_login:
        try:
            cl.album_upload(slides, caption)
            print("Puzzle uploaded to instagram")
            # Append the puzzle ID we just posted into the repeats list
            with open('repeats.csv', mode="a", newline='') as file:
                writer = csv.writer(file)
                writer.writerow(puzzle_gen.puzzle)
        except Exception as e:
            print("Failed to upload: ", e)
            if "Please wait a few minutes" in str(e):
                print("Instagram requests we wait a few minutes. Switching proxy and will try again next cycle")
                switch_proxy()

            else:
                print("Instagram terminated our session. Switching proxy and Relogging...")
                switch_proxy()
                insta_log()

    if exit_loop:
        break

    time.sleep(DELAY)
