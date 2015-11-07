from collections import deque
# TODO: Fix and re-enable colours && Make colours.py optional
import colours as clr

__author__ = 'bluabk'


clr_selection = deque(clr.pool())


def communicate(msg, module=None, facility=None, retval=False):
    if retval:
        # return "%s[%s]%s:\t %s" % (my_colour, my_name, clr.off, msg)
        if facility is None:
            return "[%s]:\t %s" % (module, msg)
        else:
            return "[%s.%s]:\t %s" % (module, facility, msg)
    else:
        # print "%s[%s]%s:\t %s" % (my_colour, my_name, clr.off, msg)
        if facility is None:
            print "[%s]:\t %s" % (module, msg)
        else:
            print "[%s.%s]:\t %s" % (module, facility, msg)


def cfg_has_sect(module, config, section):
    """
    ConfigParser has_section wrapper which prints info to shell if it fails
    :param module:
    :param config:
    :param section:
    :return:
    """
    if config.has_section(section):
        return True
    else:
        communicate("ERROR: Configuration file is missing section '%s'" % section, module, facility='config')
        return False


def cfg_has_opt(module, config, section, option):
    """
    ConfigParser has_option wrapper which prints info to shell if it fails
    :param module:
    :param config:
    :param section:
    :return:
    """
    if config.has_section(section):
        return True
    else:
        communicate("WARNING: Configuration file is missing option '%s' in section '%s'"
                    % (option, section), module, facility='config')
        return False
