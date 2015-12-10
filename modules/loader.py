import imp
import os
import re
import sys
from core import sendmsg, communicate, cfg_has_sect, cfg_has_opt, cfg as core_cfg
__author__ = 'bluabk'

#load_modules = ['triggers', 'youtube']
load_modules = ['modules.triggers', 'modules.youtube']
"""
mods_avail = list()
modules = dict()
moduleNames = None
"""
my_name = str(os.path.basename(__file__).split('.', 1)[0])
#path = os.path.abspath(os.path.dirname(sys.argv[0]))
#path = os.path.join(root_dir, 'modules') #, '%s.ini' % my_name)
root_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
#path = os.path.join(root_dir, 'modules')
path = os.path.abspath(os.path.dirname(sys.argv[0]))
#print path
#print root_dir


def import_bonanza(path, package=''):
    """
    Bonanza bonanza bonanza
    :return: S T U F F
    """
    my_name = str(os.path.basename(__file__).split('.', 1)[0])
    print my_name
    root_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    print root_dir
    #path = os.path.abspath(os.path.dirname(sys.argv[0]))
    print path
    filenameToModuleName = lambda f: os.path.splitext(f)[0]
    mods_avail = os.listdir(path)
    print "mods_avail: %s" % mods_avail
    test = re.compile("\.py$", re.IGNORECASE)
    mods_avail = filter(test.search, mods_avail)
    module_names = map(filenameToModuleName, mods_avail)
    print "module_names: " % module_names
    #modules = map(__import__, module_names)
    modules = map(__import__, load_modules)
    print "modules: %s" % modules

    return modules
