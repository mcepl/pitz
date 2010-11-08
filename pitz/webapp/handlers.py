# vim: set expandtab ts=4 sw=4 filetype=python:

import os
import re

import jinja2

class HelpHandler(object):

    def wants_to_handle(self, environ):

        """
        Return self or None.  self means this handler wants to handle
        this request.  None means it doesn't want to handle this.
        """

        if environ['PATH_INFO'] == '/help':
            return self

    def __call__(self, environ, start_response):

        """
        Return a screen of help about the web app.
        """

        # Figure out the path to the jinja2templates.
        jinja2dir = os.path.join(
            os.path.split(os.path.dirname(__file__))[0],
            'jinja2templates')

        # Set up a template loader.
        self.e = jinja2.Environment(
            extensions=['jinja2.ext.loopcontrols'],
            loader=jinja2.FileSystemLoader(jinja2dir))

        t = self.e.get_template('help.html')

        status = '200 OK'
        headers = [('Content-type', 'text/html')]

        start_response(status, headers)
        return [str(t.render(title='Pitz Webapp Help'))]


class FaviconHandler(object):

    def __init__(self):

        self.favicon_guts = open(
            os.path.join(os.path.split(os.path.dirname(__file__))[0],
            'static', 'favicon.ico')).read()

    def wants_to_handle(self, environ):

        if environ['PATH_INFO'] == '/favicon.ico':
            return self

    def __call__(self, environ, start_response):
        status = '200 OK'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)

        return [self.favicon_guts]


class StaticHandler(object):

    def wants_to_handle(self, environ):

        if environ['PATH_INFO'].startswith('/static'):
            return self

    def __call__(self, environ, start_response):

        status = '200 OK'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)

        filename = self.extract_filename(environ['PATH_INFO'])
        f = self.find_file(filename)

        return [f.read()]

    @staticmethod
    def find_file(filename):
        """
        Return an open file for filename.
        """

        return open(os.path.join(
            os.path.split(os.path.dirname(__file__))[0],
            'static', filename))

    @staticmethod
    def extract_filename(path_info):

        """
        >>> StaticHandler.extract_filename('/static/pitz.css')
        'pitz.css'
        """

        return re.match(
            r'^/static/(?P<filename>.+)$',
            path_info).groupdict()['filename']
