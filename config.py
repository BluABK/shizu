__author__ = 'bluabk'

import ConfigParser, io     # Parse configuration files, duh!


# TODO: Proper sample config
sample_config = """
[main]
nickserv-password =
pid-file = /var/run/mysqld/mysqld.pid
skip-external-locking
old_passwords = 1
skip-bdb
skip-innodb
"""

config = ConfigParser.RawConfigParser()

# When adding sections or items, add them in the reverse order of
# how you want them to be displayed in the actual file.
commentfix = """
config.add_section('samba')
config.set('irc', '', '15')

config.add_section('irc')
config.set('irc', '', '15')
config.set('irc', 'a_bool', 'true')
config.set('irc', 'a_float', '3.1415')
config.set('irc', 'baz', 'fun')
config.set('irc', 'bar', 'Python')
config.set('irc', 'foo', '%(bar)s is %(baz)s!')

# Writing our configuration file to 'example.cfg'
with open('example.cfg', 'wb') as configfile:
    config.write(configfile)
"""

config = ConfigParser.RawConfigParser(allow_no_value=True)
config.read("config.ini")

# getfloat() raises an exception if the value is not a float
# getint() and getboolean() also do this for their respective types
#a_float = config.getfloat('Section1', 'a_float')
#an_int = config.getint('Section1', 'an_int')
#print a_float + an_int

# Notice that the next output does not interpolate '%(bar)s' or '%(baz)s'.
# This is because we are using a RawConfigParser().
#if config.getboolean('Section1', 'a_bool'):
#    print config.get('Section1', 'foo')