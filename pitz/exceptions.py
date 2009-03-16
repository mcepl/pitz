# vim: set expandtab ts=4 sw=4 filetype=python:

class NoProject(Exception):
    """
    Indicates that this object can't do what you are asking it to do
    because it doesn't have a pitz.project.Project instance to work
    with.
    """
