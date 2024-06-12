"""
This script interacts with the OpenAI GPT-4o model to generate responses based on user prompts.
It provides a command-line interface for users to have conversations with the GPT-4o model.

Usage:
	python main.py [OPTIONS] [PROMPT]

Options:
	-c, --continue    Continue the previous chat

The script uses the OpenAI Python library to communicate with the GPT-4o model.
It saves the conversation history in a JSON file named 'prev_chats.json' in the same directory as the script.

Functions:
	- get_time_ms(): Returns the current time in milliseconds.
	- get_markdown(command): Runs a command in the shell and returns the output.
	- get_gpt_msg(prompt, prev_chat, is_continue=False): Generates a response from the GPT-4o model based on the prompt and previous chat history.
	- get_args(): Parses the command-line arguments and returns the prompt and is_continue flag.
	- get_prev_chat(): Retrieves the most recent chat history from the 'prev_chats.json' file.
	- save_chat(prompt, reply, time, is_continue=False): Saves the user prompt and assistant reply in the chat history.
	- continue_interface(prompt): Provides an interactive interface for continuing the chat with the GPT-4o model.
	- main(): The main entry point of the script.

Note: This script requires the OpenAI Python library and the 'glow' command-line tool to be installed.
"""

from openai import OpenAI
import sys
import subprocess
import os
import signal
import math
import re
import color as c
from utils import *
import readline  # Fixes input issues

# Setup OpenAI client
client = OpenAI()

# Formatting options for textwraps
cols = int(os.popen("stty size", "r").read().split()[1])
msg_width = cols - 10

# Menu Cursors
cursor = "◉"
cursor_empty = "◦"


def signal_handler(sig, frame):
    print(SHOW_CURSOR, end="")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def get_markdown(msg, no_wrap=False):
    """
    Run a command in the shell and return the output.
    """
    word_wrap = no_wrap == False and len(msg.strip()) > msg_width
    bubble_length = msg_width
    if not word_wrap:
        bubble_length = len(msg.strip()) + 4
    if no_wrap:
        bubble_length = cols

    try:
        # Run the command
        result = subprocess.run(
            "glow -s dark -w" + str(bubble_length),
            input=msg.strip(),
            shell=True,
            text=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # Get standard output and error
        output = result.stdout
        error = result.stderr
    except subprocess.CalledProcessError as e:
        # Handle errors in the subprocess
        output = e.stdout
        error = e.stderr

    # Remove leading white space in glow formatted lines
    formatted = []
    for line in output.split("\n"):
        formatted.append(re.sub("  ", "", line, 1))

    return "\n".join(formatted).strip()


def get_gpt_msg(prompt, prev_chat=None):
    """
    Generates a response from the GPT-4o model based on the prompt and previous chat history.
    """
    print(HIDE_CURSOR, end="")
    print(c.purple("... \r"))

    messages = [{"role": "user", "content": prompt}]

    if prev_chat:
        oai_format_prev = []
        for msg in prev_chat["messages"]:
            oai_format_prev.append({"role": msg["role"], "content": msg["content"]})
        messages = oai_format_prev + messages

    completion = client.chat.completions.create(model="gpt-4o", messages=messages)

    msg = completion.choices[0].message.content
    if prev_chat:
        save_chat(prompt, msg, get_time_ms(), prev_chat["id"])
    else:
        save_chat(prompt, msg, get_time_ms())

    clear_prompt()
    print(SHOW_CURSOR, end="")

    return msg


def get_args():
    """
    Parses the command-line arguments and returns the prompt and is_continue flag.
    """
    args = sys.argv
    arg_flags = [arg for arg in args if arg[0] == "-"]
    prompt = " ".join([arg for arg in args[1:] if arg[0] != "-"])
    is_continue = False
    is_browse = False

    for arg_flag in arg_flags:
        if arg_flag == "-c" or arg_flag == "--continue":
            is_continue = True
        elif arg_flag == "-b" or arg_flag == "--browse":
            is_browse = True
        elif arg_flag == "--clear-history":
            reset_prev_chats()
        else:
            print_header()
            print("Usage: hey [OPTIONS] [PROMPT]")
            print("Options:")
            print("  -b, --browse     Choose a previous chat to continue from")
            print("  -c, --continue   Continue the previous chat")
            print("  --clear-history  Removes all previous chats")
            sys.exit(0)

    return prompt, is_continue, is_browse


def print_time(time, right_align=False):
    time_str = get_formatted_datetime(time)

    # I made the bar invisible as it wa a little distracting
    bar = c.grey(" " * (cols - 10 - len(time_str) - 1))
    padding = " " * 10
    if right_align:
        print(padding + bar + " " + c.yellow(time_str))
    else:
        print(c.yellow(time_str + " " + bar))


def print_ai_msg(msg, time):
    print("")
    print_time(time)

    print(get_markdown(msg))


def print_user_msg(msg, time):
    print("")
    print_time(time, True)

    md = get_markdown(msg)
    if "\n" in md:
        for line in md.split("\n"):
            print(" " * (cols - msg_width - 1), line)
    else:
        print(" " * (cols - get_visible_length(md) - 1), md)


def print_header():
    print(c.bold(c.purple_bg(" hey ")))
    print(c.grey("Your personal terminal assistant"))
    print("")


def print_prev_chats(selected):
    print_header()

    # Read the original data
    chats = get_saved_chats()

    # if no prev chats, show msg
    if len(chats) == 0:
        margin = math.floor((cols - 24) / 2) * " "
        print(margin + c.grey("No previous chats found.") + margin)

    index = 1
    available_indexes = []
    ids = []
    max_preview_len = cols - 40
    for chat in chats:
        msgs = chat["messages"]
        print(
            (
                (
                    c.green(cursor + " ")
                    if selected == index - 1
                    else c.grey(cursor_empty + " ")
                )
                if selected != None
                else ""
            )
            + c.grey(get_formatted_datetime(msgs[0]["time"])),
            "",
            msgs[0]["content"][0:max_preview_len]
            + ("..." if len(msgs[0]["content"]) > max_preview_len else "   "),
            " " * (max_preview_len - len(msgs[0]["content"][0:max_preview_len])),
            c.grey("(" + str(len(msgs)) + ")") if len(msgs) > 2 else "",
        )
        available_indexes.append(str(index))
        ids.append(chat["id"])
        index += 1

    padding = round((cols - 18) / 3) * " "
    print(c.purple("\n" + padding + "(n)ew chat" + padding + "(q)uit\n"))

    return available_indexes, ids


def browse_interface():
    """
    Prompt interface, printing previous
    """
    new_chat = False
    position = 0
    choice = 0

    print(HIDE_CURSOR)
    available_indexes, ids = print_prev_chats(position)

    while True:
        num_options = len(available_indexes)
        key = get_key()

        if key == "\x1b":  # Handle escape sequences
            key += get_key()
            key += get_key()

        if key == "\x1b[A":  # Up arrow
            position = max(0, position - 1)
            clear_n_lines(len(available_indexes) + 6)
            available_indexes, ids = print_prev_chats(position)
        elif key == "\x1b[B":  # Down arrow
            position = min(num_options - 1, position + 1)
            clear_n_lines(len(available_indexes) + 6)
            available_indexes, ids = print_prev_chats(position)
        elif key == "\n" or key == "\r":  # Select Option
            clear_n_lines(len(available_indexes) + 8)
            choice = position
            break
        elif key == "q":  # Quit with 'q'
            clear_n_lines(len(available_indexes) + 8)
            print(SHOW_CURSOR)
            return
        elif key == "n":  # new chat with 'n
            clear_n_lines(len(available_indexes) + 7)
            new_chat = True
            break

    print(SHOW_CURSOR)
    if new_chat:
        continue_interface(is_new=True)
    else:
        continue_interface(chat_id=ids[choice])


def continue_interface(prompt="", chat_id=None, is_new=False):
    """
    Provides an interactive interface for continuing the chat with the GPT-4o model.
    """

    prev_chat = get_prev_chat(chat_id) if not is_new else None
    has_quit = False

    if is_new:
        centre = " New Chat "
    else:
        centre = (
            " Chat from " + get_formatted_date(prev_chat["messages"][-1]["time"]) + " "
        )

    bar = " " * math.floor((cols - len(centre)) / 2)

    print(c.grey(bar + centre + bar))

    if not is_new:
        # Print the previous messages
        for msg in prev_chat["messages"]:
            if msg["role"] == "user":
                print_user_msg(msg["content"], msg["time"])
            if msg["role"] == "assistant":
                print_ai_msg(msg["content"], msg["time"])

    if len(prompt) > 0:
        print_user_msg(prompt, get_time_ms())

        msg = get_gpt_msg(prompt, prev_chat)
        print_ai_msg(msg, get_time_ms())

    while not has_quit:
        prompt = user_input()
        clear_prompt()

        if prompt == "quit" or prompt == "q" or prompt == "exit":
            has_quit = True
            print_goodbye()
            continue

        print_user_msg(prompt, get_time_ms())

        msg = get_gpt_msg(prompt, prev_chat)
        print_ai_msg(msg, get_time_ms())


def main():
    """
    The main entry point of the script.
    """
    # makes chat history json store if its missing
    init_prev_chats()

    # nicely formats args and prints help if needed
    prompt, is_continue, is_browse = get_args()

    # If the continue flag is passed, jump straight in there
    if is_continue:
        continue_interface(prompt)

    # If the browse flag is passed, or the user didnt pass anything
    elif is_browse or prompt.strip() == "":
        browse_interface()

    # If the user has passed text, we generate a message
    # and give it back with no interface
    else:
        msg = get_gpt_msg(prompt, None)
        print(get_markdown(msg, no_wrap=True))


if __name__ == "__main__":
    main()