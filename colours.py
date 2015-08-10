__author__ = 'BluABK <abk@blucoders.net'

# This is a module specification, which contains everything you need to get started on writing a module.

# Imports
import ConfigParser

# Variables
commandsavail = "wishfulthinking, pipedreams, 42, imagination"

# Classes


class Config:  # Mandatory Config class
    config = ConfigParser.RawConfigParser()

    def __init__(self):
        print "[modules/colours]:\t Initiating config..."
        self.config.read('config.ini')

    def sample(self):
        return str(self.config.get('sample', 'sampleitem'))

cfg = Config()

# Functions

# Reset
off = '\e[0m'                           # Text Reset

# Regular Colors
black = '\e[0;30m'                  # Black
red = '\e[0;31m'                    # Red
green = '\e[0;32m'                  # Green
yellow = '\e[0;33m'                 # Yellow
blue = '\e[0;34m'                   # Blue
purple = '\e[0;35m'                 # Purple
cyan = '\e[0;36m'                   # Cyan
white = '\e[0;37m'                  # White

# Bold
bold_black = '\e[1;30m'             # Black
bold_red = '\e[1;31m'               # Red
bold_green = '\e[1;32m'             # Green
bold_yellow = '\e[1;33m'            # Yellow
bold_blue = '\e[1;34m'              # Blue
bold_purple = '\e[1;35m'            # Purple
bold_cyan = '\e[1;36m'              # Cyan
bold_white = '\e[1;37m'             # White

# Underline
uline_black = '\e[4;30m'            # Black
uline_red = '\e[4;31m'              # Red
uline_green = '\e[4;32m'            # Green
uline_yellow = '\e[4;33m'           # Yellow
uline_blue = '\e[4;34m'             # Blue
uline_purple = '\e[4;35m'           # Purple
uline_cyan = '\e[4;36m'             # Cyan
uline_white = '\e[4;37m'            # White

# Background
bg_black = '\e[40m'                 # Black
bg_red = '\e[41m'                   # Red
bg_green = '\e[42m'                 # Green
bg_yellow = '\e[43m'                # Yellow
bg_blue = '\e[44m'                  # Blue
bg_purple = '\e[45m'                # Purple
bg_cyan = '\e[46m'                  # Cyan
bg_white = '\e[47m'                 # White

# High Intensity
intense_black = '\e[0;90m'          # Black
intense_red = '\e[0;91m'            # Red
intense_green = '\e[0;92m'          # Green
intense_yellow = '\e[0;93m'         # Yellow
intense_blue = '\e[0;94m'           # Blue
intense_purple = '\e[0;95m'         # Purple
intense_cyan = '\e[0;96m'           # Cyan
intense_white = '\e[0;97m'          # White

# Bold High Intensity
intense_bold_black = '\e[1;90m'     # Black
intense_bold_red = '\e[1;91m'       # Red
intense_bold_green = '\e[1;92m'     # Green
intense_bold_yellow = '\e[1;93m'    # Yellow
intense_bold_blue = '\e[1;94m'      # Blue
intense_bold_purple = '\e[1;95m'    # Purple
intense_bold_cyan = '\e[1;96m'      # Cyan
intense_bold_white = '\e[1;97m'     # White

# High Intensity backgrounds
intense_bg_black = '\e[0;100m'      # Black
intense_bg_red = '\e[0;101m'        # Red
intense_bg_green = '\e[0;102m'      # Green
intense_bg_yellow = '\e[0;103m'     # Yellow
intense_bg_blue = '\e[0;104m'       # Blue
intense_bg_purple = '\e[0;105m'     # Purple
intense_bg_cyan = '\e[0;106m'       # Cyan
intense_bg_white = '\e[0;107m'      # White


def helpcmd(cmdsym):
    cmdlist = list()
    cmdlist.append("Syntax: %scommand help arg1..argN" % cmdsym)
    cmdlist.append("Available commands: %s (* command contains sub-commands)" % commandsavail)
    return cmdlist
