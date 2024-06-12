from colorama import Fore, Style, init, Back


# Initialise Colorama
init()


def bold(str):
    return Style.BRIGHT + str + Style.RESET_ALL


def white(str):
    return Fore.WHITE + str + Style.RESET_ALL


def yellow(str):
    return Fore.YELLOW + str + Style.RESET_ALL


def red(str):
    return Fore.RED + str + Style.RESET_ALL


def grey(str):
    return Fore.LIGHTBLACK_EX + str + Style.RESET_ALL


def green(str):
    return Fore.GREEN + str + Style.RESET_ALL


def cyan(str):
    return Fore.CYAN + str + Style.RESET_ALL


def purple(str):
    return Fore.MAGENTA + str + Style.RESET_ALL


def blue(str):
    return Fore.BLUE + str + Style.RESET_ALL


def purple_bg(str):
    return Fore.BLACK + Back.MAGENTA + str + Style.RESET_ALL


def red_bg(str):
    return Fore.WHITE + Back.RED + str + Style.RESET_ALL


def black_bg(str):
    return Fore.WHITE + Back.BLACK + str + Style.RESET_ALL
