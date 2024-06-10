import pandas as pd
import color as c
import sys
import termios
import tty
import re
import datetime 
import random
                                                            
CLEAR_RIGHT = "\033[K"  # clean to the right of the cursor
PREV_LINE = "\033[F"  # move cursor to the beginning of previous line
HIDE_CURSOR = "\033[?25l" # hide cursor
SHOW_CURSOR = "\033[?25h" # show cursor


def get_time_ms():
	return int(datetime.datetime.now().timestamp() * 1000)


def clear_prompt():
	print(f"{PREV_LINE}{CLEAR_RIGHT}")


def get_formatted_date(ms):
	utc_time = pd.to_datetime(ms, unit='ms', utc=True)
	local_time = utc_time.tz_convert('Pacific/Auckland')
	return local_time.strftime("%d %b'%y")


def get_formatted_datetime(ms):
    utc_time = pd.to_datetime(ms, unit='ms', utc=True)
    local_time = utc_time.tz_convert('Pacific/Auckland')
    ampm = local_time.strftime("%p").lower()

    return local_time.strftime("%d %b'%y %I:%M") + ampm


def user_input():
	result = input(c.bold(c.purple("\n> \n\033[1A\033[2C")))
	clear_prompt()
	print("\033[2A")
	return result


def get_visible_length(s):
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    stripped_string = ansi_escape.sub('', s)
    return len(stripped_string)


def clear_n_lines(n):
    # Move the cursor up `n` lines
    for _ in range(n):
        # Move cursor up one line
        sys.stdout.write('\033[F')
        # Clear the line
        sys.stdout.write('\033[K')

def print_goodbye():
    goodbye_phrases = [                                                          
        "See you later",
        "Catch you later",
        "Smell you later",
        "See ya loser",
        "Bye for now",
        "Peace out",
        "Talk to you later",
        "So long",
        "Adios",
        "Ciao",
        "See you around",
        "Until our paths cross again",
        "Godspeed",
        "Don't do anything I would do",
    ]

    if random.randint(0,20) == 0:
        print("👉😎👉")
    
    print(random.choice(goodbye_phrases) + " 👋")


def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        if ch == '\x1b':  # Handle escape sequences
            ch += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch