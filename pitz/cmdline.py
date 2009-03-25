# vim: set expandtab ts=4 sw=4 filetype=python:

from IPython.Shell import IPShellEmbed
from pitz import *

def shell():

    p = Project('Pitz', 
        '/home/matt/projects/pitz/pitz/.pitz')

    s = IPShellEmbed(['-colors', 'Linux'])
    s()

    answer = raw_input("Write out updated yaml files? (y/[n]) ")
    if answer.lower() in ['y', 'yes']:
        p.to_yaml_files()

