# vim: set expandtab ts=4 sw=4 filetype=python:

import logging
from wsgiref.simple_server import make_server

import pitz
from pitz.cmdline import setup_options
from pitz.project import Project

from pitz import webapp
from pitz.webapp import handlers

def pitz_webapp():

    """
    Later on, will be awesome.
    """

    p = setup_options()

    options, args = p.parse_args()
    pitz.setup_logging(getattr(logging, options.log_level))

    if options.version:
        print_version()
        return

    pitzdir = Project.find_pitzdir(options.pitzdir)

    proj = Project.from_pitzdir(pitzdir)
    proj.find_me()

    app = webapp.SimpleWSGIApp(proj)

    # Remember that the order that you add handlers matters.  When a
    # request arrives, the app starts with the first handler added and
    # asks it if wants to handle that request.  So, the default handler
    # (if you make one) belongs at the end.
    app.handlers.append(handlers.FaviconHandler())
    app.handlers.append(handlers.StaticHandler())
    app.handlers.append(handlers.HelpHandler())
    app.handlers.append(handlers.ByFragHandler(proj))
    app.handlers.append(handlers.Project(proj))

    httpd = make_server('', 8000, app)
    print "Serving on port 8000..."
    httpd.serve_forever()