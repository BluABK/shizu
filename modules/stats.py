# This is a module specification, which contains everything you need to get started on writing a module.

# Imports
import ConfigParser
import os

import colours as clr

try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
except (ImportError, ImportWarning) as e:
    print "[stats/import]:\t ERROR: Unable to import wordcloud, feature will be disabled.\nDetails: %s" % e
    WordCloud = None
    plt = None

__author__ = 'BluABK <abk@blucoders.net'

# Variables
my_name = os.path.basename(__file__).split('.', 1)[0]
my_colour = clr.purple
commandsavail = "user, command, dump"


# Classes
class Config:  # Mandatory Config class
    config = ConfigParser.RawConfigParser()

    def __init__(self):
        print "%s[%s]%s:\t Initiating config..." % (my_colour, my_name, clr.off)
        self.config.read('config.ini')

    # def __call__(self):
    #    self.config.read('config.ini')

    #    def loadconfig(self):
    #        configloc = os.getcwd() + '/' + "config.ini"
    #        print(configloc)
    #        self.config.read(configloc)
    #        return True

    def get_cmd(self, name):
        return int(self.config.get('stats-cmd', name))

    def get_user(self, user):
        return [str(self.config.get('stats-user', str(user) + '-cmd')),
                int(self.config.get('stats-user', str(user) + '-num'))]

    def update_cmd(self, cmd, num):
        try:
            self.config.read('config.ini')
            if self.config.has_option('stats-cmd', str(cmd)) is False:
                self.config.set('stats-cmd', str(cmd), str(num))
                with open('config.ini', 'w') as configfile:
                    self.config.write(configfile)
                retv = "Updated num and cmd"
            else:
                self.config.set('stats-cmd', str(cmd), str(self.get_cmd(cmd) + num))
                with open('config.ini', 'w') as configfile:
                    self.config.write(configfile)
                retv = "Updated num"
        except:
            retv = "Unable to open configuration"

        print ('\033[94mstats.py: update_cmd(%s, %s):\033[0m %s' % (cmd, num, retv))
        return retv

    def update_user(self, user, cmd, num):
        try:
            self.config.read('config.ini')
            if self.config.has_option(str(user) + 'cmd', str(cmd)) is False:
                self.config.set('stats-user', str(user) + '-cmd', str(cmd))
                self.config.set('stats-user', str(user) + '-num', str(num))
                with open('config.ini', 'w') as configfile:
                    self.config.write(configfile)
                retv = "Updated num and cmd"

            else:
                cnt = 0
                for c in self.config.get('stats-user', str(user) + '-cmd').split(","):
                    if c == cmd:
                        break
                    cnt += 1
                sl = self.config.get('stats-user', str(user) + '-num').split(",")
                sl[cnt] += num
                s = sl.toString()
                self.config.set('stats-user', str(user) + '-num', s)
                with open('config.ini', 'w') as configfile:
                    self.config.write(configfile)
                retv = "Updated num"
        except:
            retv = "Unable to open configuration"

        print ('\033[94mstats.py: update_user(%s, %s, %s):\033[0m %s' % (user, cmd, num, retv))
        return retv

    def dump_cmd(self):
        return self.config.items('stats-cmd')


cfg = Config()


# if WordCloud is not None:


# Functions
def update_user(user, cmd, num):
    return cfg.update_user(str(user), str(cmd), int(num))


def update_cmd(cmd, num):
    return cfg.update_cmd(str(cmd), int(num))


def get_user(user):
    return cfg.get_user(str(user))


def get_cmd(cmd):
    return cfg.get_cmd(str(cmd))


def get_cmd_all():
    return cfg.dump_cmd()


#TODO: Implement
def wc_generate(mode):
    if WordCloud is None or plt is None:
        # Die immediately if wordcloud or matplot module is not present
        return

    if mode is "commands":
        text = None
        text = cfg.dump_cmd()
        # Generate a word cloud image
        wordcloud = WordCloud().generate(text)

        # Produce plot
        plt.imshow(wordcloud)
        plt.axis("off")

        # take relative word frequencies into account, lower max_font_size
        wordcloud = WordCloud(max_font_size=40, relative_scaling=.5).generate(text)
        plt.figure()
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.show()



def helpcmd(cmdsym):
    cmdlist = list()
    cmdlist.append("Syntax: %scommand help arg1..argN" % cmdsym)
    cmdlist.append("Available commands: %s (* command contains sub-commands)" % commandsavail)
    return cmdlist
