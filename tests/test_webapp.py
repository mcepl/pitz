# vim: set expandtab ts=4 sw=4 filetype=python:

import os
import unittest
import urllib

import mock

from pitz.project import Project

from pitz.entity import Entity, Person, Task, Status, Milestone, \
Activity, Estimate, Tag, Comment, Component

from pitz.webapp import HelpHandler, SimpleWSGIApp

class TestWebApp(unittest.TestCase):

    def setUp(self):

        self.p = Project(title='Bogus project for testing webapp')
        c = Entity(self.p, title="c")
        Entity(self.p, title="t")
        matt = Person(self.p, title='matt')
        self.webapp = SimpleWSGIApp(self.p)
        self.webapp.handlers.append(HelpHandler())

        Status(self.p, title='bogus status')
        Estimate(self.p, title='bogus estimate')
        Milestone(self.p, title='bogus milestone')
        Tag(self.p, title='bogus tag')
        Task(self.p, title='bogus task')
        Component(self.p, title='bogus component')

        Comment(
            self.p,
            title='bogus comment',
            who_said_it=matt,
            entity=c)

        Activity(
            self.p,
            title='bogus activity',
            who_did_it=matt, entity=c)

    def tearDown(self):

        for e in self.p:
            e.self_destruct(self.p)

        if os.path.exists('/tmp/project.pickle'):
            os.remove('/tmp/project.pickle')

    def mk_request(self, pi, qs, ha, expected_status,
        expected_results=None):

        bogus_environ = dict(
            PATH_INFO=pi,
            QUERY_STRING=qs,
            HTTP_ACCEPT=ha)

        bogus_start_response = mock.Mock()
        results = self.webapp(bogus_environ, bogus_start_response)

        assert bogus_start_response.called
        assert bogus_start_response.call_args[0][0] == expected_status

        if expected_results:
            assert results == [expected_results], results

        return results


    def test_1(self):
        self.mk_request('/', '', 'text/plain', '200 OK',
            self.p.detailed_view)

    def test_2(self):
        self.mk_request('/', 'title=c', 'text/plain',
            '200 OK',
            self.p.matches_dict(title='c').detailed_view)

    def test_3(self):
        self.mk_request('/', 'title=c&title=t', 'text/plain',
            '200 OK',
            self.p.matches_dict(title=['c', 't']).detailed_view)

    def test_4(self):
        self.mk_request('/', 'title=c&title=t', 'application/x-pitz',
            '200 OK',
            self.p.matches_dict(title=['c', 't']).colorized_detailed_view)

    def test_5(self):
        self.mk_request('/Entity/by_title/c', '', 'text/plain',
            '200 OK',
            str(Entity.by_title('c')))

    def test_6(self):
        self.mk_request('/Task/all/detailed_view', 'status=unstarted',
            'text/plain',
            '200 OK',
            Task.all().matches_dict(
                status=['unstarted']).detailed_view)

    def test_7(self):
        self.mk_request('/Person/by_title/matt/my_todo', '',
            'text/plain',
            '200 OK',
            Person.by_title('matt').my_todo.detailed_view)

    def test_8(self):
        self.mk_request('/Person/by_title/matt/my_todo/summarized_view',
            '', 'text/plain',
            '200 OK',
            Person.by_title('matt').my_todo.summarized_view)

    def test_9(self):
        self.mk_request('/',
            'owner=matt&owner=lindsey',
            'text/plain',
            '200 OK',
            str(self.p(owner=['matt', 'lindsey'])))


    def test_11(self):
        matt = Person.by_title('matt')

        self.mk_request('/by_frag/%s/my_todo' % matt.frag,
            '',
            'text/plain',
            '200 OK',
            str(matt.my_todo))

        self.mk_request('/by_frag/%s/my_todo/summarized_view' % matt.frag,
            '',
            'text/plain',
            '200 OK',
            str(matt.my_todo.summarized_view))

        self.mk_request('/by_frag/%s/my_todo/detailed_view' % matt.frag,
            '',
            'text/plain',
            '200 OK',
            str(matt.my_todo.detailed_view))


    def test_12(self):

        m = self.p.milestones[0]

        self.mk_request('/by_frag/%s/my_todo' % m.frag,
            '',
            'text/plain',
            '404 NOT FOUND',
            """Sorry, didn't match any patterns...""")


    def test_help(self):

        self.mk_request('/help',
            '',
            'text/plain',
            '200 OK',
            '')

class TestHelpHandler(unittest.TestCase):

    def setUp(self):
        self.hh = HelpHandler()

    def test_1(self):
        help_page_iterable = self.hh(mock.Mock(), mock.Mock())


class TestDispatcher(unittest.TestCase):

    def setUp(self):
        self.p = Project(title='Bogus project for testing webapp')
        self.app = SimpleWSGIApp(self.p)
        self.app.handlers = []

        self.bogus_environ = dict(
            PATH_INFO='/fibityfoo',
            QUERY_STRING='?a=1')

    def test_1(self):
        """
        Make sure nothing blows up when nothing matches.
        """

        assert self.app.dispatch(self.bogus_environ) is None

