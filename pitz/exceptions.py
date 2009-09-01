# vim: set expandtab ts=4 sw=4 filetype=python:

class PitzException(Exception):
    """
    All pitz exceptions subclass this guy.
    """

class NoProject(PitzException):
    """
    Indicates that this object can't do what you are asking it to do
    because it doesn't have a pitz.project.Project instance to work
    with.
    """

class ProjectNotFound(PitzException):
   """
    Indicates that the system couldn't find what it needed to create a
    project.
    """
