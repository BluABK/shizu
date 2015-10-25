__author__ = 'bluabk'

# The following is ideas that have either been put off or dropped entirely, don't expect any sense of order though..

# TODO: Make module loading dynamic

comment = """
def modulecommands(usrnick, msg, chan, modlist):
    for i in range(len(modules)):
        getattr(modlist[i], 'modcommands')(usrnick, msg, chan)

"""

comment = """
def getmodules():
    mod_dir = "modules/"
    curdir = os.getcwd()
    modlist = os.listdir(mod_dir)
    print(modlist)
    modulelist = []
    os.chdir(mod_dir)
    for mod in modlist:
        print(mod[:-3])
        if mod[:-3] != "__init__":
            modulelist.append(mod[:-3])
    os.chdir(curdir)
    return modulelist


def loadmodules(modlist):
    for i in range(len(modlist)):
        print modlist[i]
        __import__('modules.' + str(modlist[i]))

modules = getmodules()
loadmodules(modules)
"""
