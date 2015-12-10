import imp
import os
import re
import sys
from core import sendmsg, communicate, cfg_has_sect, cfg_has_opt, cfg as core_cfg
import modules.loader as loader
__author__ = 'bluabk'

load_modules = ['triggers', 'youtube']
"""
mods_avail = list()
modules = dict()
moduleNames = None
"""
my_name = str(os.path.basename(__file__).split('.', 1)[0])
#path = os.path.abspath(os.path.dirname(sys.argv[0]))
filenameToModuleName = lambda f: os.path.splitext(f)[0]
#path = os.path.join(root_dir, 'modules') #, '%s.ini' % my_name)
root_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
path = os.path.join(root_dir, 'modules')
#print path
#print root_dir


# def import_bonanza():
#    """
#    Bonanza bonanza bonanza
#    :return: S T U F F
#    """
#    global mods_avail, moduleNames
"""
mods_avail = os.listdir(path)
print mods_avail
test = re.compile("triggers\.py$", re.IGNORECASE)
mods_avail = filter(test.search, mods_avail)
moduleNames = map(filenameToModuleName, mods_avail)
print moduleNames
modules = map(__import__, 'modules.%s' % moduleNames)
print modules
"""
print "path: %s" % path
modules = loader.import_bonanza(path)


def module_exists(module_name):
    try:
        imp.find_module("modules.%s" % module_name)
        return True
    except ImportError:
        communicate("WARNING: Unable to import module: %s" % module_name, my_name, facility='import')
        return False


def import_module(module_name):
    """
    Imports module_name if module_exists(modules.module_name)
    :param module_name: str
    :return: imported module or None
    """
    # if module_exists("modules.%s" % module_name) is True:
    if True:
        mods_avail.append(module_name)
        #mods_avail.update({module_name: })
        #return __import__("modules.%s" % module_name)
        # import Python Object as a bytestring
        #exec(('%s=%s') % (module_name,  __import__("modules.%s" % module_name)))
        dat_pesky_bastard = __import__("modules.%s" % module_name)
        #exec(('%s=%s') % (module_name, dat_pesky_bastard))
        print locals()
        #print vars(dat_pesky_bastard)
        return dat_pesky_bastard
        # Convert back into a Python Object
        #eval(module_name)
    else:
        return None
"""
# Import modules
for m in load_modules:
    modules.update({m: import_module(m)})
    #mods_avail.append(m)
"""

#import_bonanza()

#print mods_avail
print modules
print modules[0]
print modules[0].triggers
exec(load_modules[0] + "= None")
print triggers
print type(load_modules[0])
triggers = modules[0].triggers
#eval(load_modules[0]) = modules[0].triggers
print triggers
a = {}
#a.update({: modules[0]})
#exec(('%s=%s') % (modules[0], dat_pesky_bastard))
#a = map(['triggers', 'youtube'], modules)
#print a

#print modules

modules[0].triggers.test()
#sys.__module__()
#triggers.test()

#print modules["triggers"]

#getattr(modules['triggers'], 'my_name')
