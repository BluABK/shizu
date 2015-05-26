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
        self.config.read('config.ini')

#    def loadconfig(self):
#        configloc = os.getcwd() + '/' + "config.ini"
#        print(configloc)
#        self.config.read(configloc)
#        return True

    def get_cmd(self, name):
        return int(self.config.get('stats-cmd', name))

    def get_user(self, user):
        return [str(self.config.get('stats-user', str(user)+'-cmd')),
                int(self.config.get('stats-user', str(user)+'-num'))]

    def update_cmd(self, cmd, num):
        try:
            config = Config.config
            if self.config.has_option('stats-cmd', str(cmd)) is False:
                config.set('stats-cmd', str(cmd), str(num))
                with open('config.ini', 'w') as configfile:
                        config.write(configfile)
                retv = "Updated num and cmd"
            else:
                config.set('stats-cmd', str(cmd), str(self.get_cmd(cmd)+num))
                with open('config.ini', 'w') as configfile:
                        config.write(configfile)
                retv = "Updated num"
        except:
            retv = "Unable to open configuration"

        return retv

    def update_user(self, user, cmd, num):
        try:
            config = Config.config
            if self.config.has_option(str(user)+'cmd', str(cmd)) is False:
                    config.set('stats-user', str(user)+'-cmd', str(cmd))
                    config.set('stats-user', str(user)+'-num', str(num))
                    with open('config.ini', 'w') as configfile:
                        config.write(configfile)
                    retv = "Updated num and cmd"

            else:
                config.set('stats-user', str(user)+'-num', str(self.get_user(user)[1]+num))
                with open('config.ini', 'w') as configfile:
                        config.write(configfile)
                retv = "Updated num"
        except:
            retv = "Unable to open configuration"

        return retv

cfg = Config()

# Functions


def helpcmd(cmdsym):
    cmdlist = list()
    cmdlist.append("Syntax: %scommand help arg1..argN" % cmdsym)
    cmdlist.append("Available commands: %s (* command contains sub-commands)" % commandsavail)
    return cmdlist