import pandas as pd
import color as c
import sys
import termios
import tty
import re
import datetime
import random
import json
import uuid
import os

CLEAR_RIGHT = "\033[K"  # clean to the right of the cursor
PREV_LINE = "\033[F"  # move cursor to the beginning of previous line
HIDE_CURSOR = "\033[?25l"  # hide cursor
SHOW_CURSOR = "\033[?25h"  # show cursor

# Save location for previous chats
script_dir = os.path.dirname(os.path.abspath(__file__))
data_json_path = file_path = os.path.join(script_dir, "prev_chats.json")


# Data Loading Utils ============================================================


def init_prev_chats():
    if not os.path.exists(data_json_path):
        with open(data_json_path, "w") as f:
            json.dump([], f)


def reset_prev_chats():
    with open(data_json_path, "w") as f:
        json.dump([], f)


def get_saved_chats():
    chats = []
    if os.path.exists(data_json_path):
        with open(data_json_path, "r") as f:
            chats = json.load(f)

    # Sort by most recently updated
    chats = sorted(chats, key=lambda chat: chat["messages"][-1]["time"])
    chats.reverse()

    return chats


def get_prev_chat(chat_id=None):
    """
    Retrieves the most recent chat history from the 'prev_chats.json' file.
    """
    # Read the original data
    chats = []
    if os.path.exists(data_json_path):
        with open(data_json_path, "r") as f:
            chats = json.load(f)

    if chat_id:
        # Find the chat with the given ID
        for chat in chats:
            if chat["id"] == chat_id:
                return chat
    else:
        # Find the most recent chat
        most_recent_chat = chats[0]
        for chat in chats[1:]:
            if chat["messages"][-1]["time"] > most_recent_chat["messages"][-1]["time"]:
                most_recent_chat = chat

        return most_recent_chat


def save_chat(prompt, reply, time, prev_id=None):
    """
    Saves the user prompt and assistant reply in the chat history.
    """
    # Read the original data
    chats = []
    if os.path.exists(data_json_path):
        with open(data_json_path, "r") as f:
            chats = json.load(f)

    if prev_id:
        # Find the most recent chat
        prev_chat = None
        for chat in chats:
            if chat["id"] == prev_id:
                prev_chat = chat
                break

        # Append the new data
        prev_chat["messages"].append(
            {"role": "user", "content": prompt, "time": time},
        )
        prev_chat["messages"].append(
            {"role": "assistant", "content": reply, "time": time}
        )

    else:
        # Append the new data
        chats.append(
            {
                "id": str(uuid.uuid4()),
                "messages": [
                    {"role": "user", "content": prompt, "time": time},
                    {"role": "assistant", "content": reply, "time": time},
                ],
            }
        )

    # Write the new data
    with open(data_json_path, "w") as f:
        json.dump(chats, f)


# Generic Utils ==================================================================


def get_time_ms():
    return int(datetime.datetime.now().timestamp() * 1000)


def clear_prompt():
    print(f"{PREV_LINE}{CLEAR_RIGHT}")


def get_formatted_date(ms):
    utc_time = pd.to_datetime(ms, unit="ms", utc=True)
    local_time = utc_time.tz_convert("Pacific/Auckland")
    return local_time.strftime("%d %b'%y")


def get_formatted_datetime(ms):
    utc_time = pd.to_datetime(ms, unit="ms", utc=True)
    local_time = utc_time.tz_convert("Pacific/Auckland")
    ampm = local_time.strftime("%p").lower()

    return local_time.strftime("%d %b'%y %I:%M") + ampm


def user_input():
    result = input(c.bold(c.purple("\n> \n\033[1A\033[2C")))
    clear_prompt()
    print("\033[2A")
    return result


def get_visible_length(s):
    ansi_escape = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")
    stripped_string = ansi_escape.sub("", s)
    return len(stripped_string)


def has_recent_conversation():
    """
    If the last conversation was < 1 min ago, we auto continue
    """
    chats = get_saved_chats()
    if chats[0]["time"] < (get_time_ms() - 1000 * 60):
        return True
    else:
        return False


def clear_n_lines(n):
    # Move the cursor up `n` lines
    for _ in range(n):
        # Move cursor up one line
        sys.stdout.write("\033[F")
        # Clear the line
        sys.stdout.write("\033[K")


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

    if random.randint(0, 20) == 0:
        print("👉😎👉")
    else:
        print(random.choice(goodbye_phrases) + " 👋")


def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        if ch == "\x1b":  # Handle escape sequences
            ch += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch
