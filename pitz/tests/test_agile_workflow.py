# vim: set expandtab ts=4 sw=4 filetype=python:

"""
Verify we can use pitz for an agile workflow, where "agile" means:

* one project has many releases.
* each release has one or more iterations.
* each iteration has numerous user stories.
* each story has numerous tasks.
"""

from nose.tools import raises, with_setup

from pitz.projecttypes.agilepitz import *

ap = None

def setup():

    global ap
    ap = AgileProject()
    ap.append(UserStory(title='Draw new accounting report', priority=2))
    ap.append(UserStory(title='Improve speed of search page', priority=0))

    ap.append(UserStory(title='Add animation to site logo',
        estimate=2))

    ap.append(UserStory(title='Write "forgot password?" feature',
        priority=1, estimate=2))

    ap.append(UserStory(title='Allow customer to change contact information',
        priority=2, estimate=2))

    ap.append(UserStory(title='Allow customer to change display name',
        priority=2, estimate=1))


def test_show_backlog_1():
    """
    List every user story in the backlog, ordered by priority.
    """

    global ap
    assert len(ap.backlog) == 6


def test_show_backlog_2():
    """
    Only list the estimated stories in the backlog, ordered by priority.
    """

    global ap
    assert len(ap.estimated_backlog) == 4

def test_show_backlog_3():
    """
    Only list unestimated stories in the backlog, ordered by priority.
    """

    global ap
    b = ap.backlog(estimate='unknown')
    assert len(b) == 2
    assert b[0]['priority'] <= b[1]['priority']


def test_estimate_story_1():

    """
    Create tasks for a story and then add an estimate to the story.
    """

    global ap
    us = ap.backlog(estimate='unknown')[0]
    assert us in ap.backlog(estimate='unknown')
    ap.append(Task(title="Get mockups approved", story=us))
    ap.append(Task(title="Write queries", story=us))
    ap.append(Task(title="Write some tests", story=us))
    us['estimate'] = 2
    assert us not in ap.backlog(estimate='unknown')

@with_setup(setup)
def test_add_story_1():

    """
    Add a single story to an iteration.
    """

    global ap
    ap.order()
    it99 = Iteration(ap, title="Iteration for week 99", velocity=5)
    s = ap.estimated_backlog[0]

    assert s['status'] == 'backlog', \
    "status for %(title)s is %(status)s!" % s

    it99.add_story(s)

    assert s['status'] == 'planned', \
    "status for %(title)s is %(status)s!" % s
    
    assert len(it99.stories) == 1
    assert len(it99.stories) == 1

    assert it99.stories[0] == s

    assert it99.points == s.points
    assert it99.slack == it99.velocity - s.points


def test_plan_iteration_1():
    """
    Figure out what user stories can fit into the next release.
    """

    global ap

    ap.order()

    it99 = Iteration(ap, title="Iteration for week 99", velocity=5)
    print("it99 has %d points of slack." % it99.slack)

    it99.plan_iteration()

    assert it99.points == it99['velocity']
    assert not it99.slack

    for s in it99.stories:
        assert s['iteration'] == it99
        assert s['status'] == 'planned'
    

@with_setup(setup)
def test_plan_iteration_2():
    """
    Plan the next two iterations.
    """

    global ap
    ap.order()
    it99 = Iteration(ap, title="Iteration for week 99", velocity=5)
    it99.plan_iteration()

    assert len(it99.stories) == 3

    it100 = Iteration(ap, title="Iteration for week 100", velocity=5)
    it100.plan_iteration()

    assert len(it100.stories) == 1


@with_setup(setup)
def test_plan_iteration_3():
    """
    Take something out of an iteration in order to make room for
    something else.
    """

    global ap

    ap.order()

    it99 = Iteration(ap, title="Iteration for week 99", velocity=5)

    it99.plan_iteration()

    assert it99.points == it99['velocity']
    assert not it99.slack

    s1, s2, s3 = it99.stories
    s2.send_to_backlog()

    assert it99.slack, "it99.slack is %s" % it99.slack


@raises(Exception)
@with_setup(setup)
def test_add_story_2():
    """
    Try to add another story after using up the slack.
    """

    global ap
    ap.order()
    it99 = Iteration(ap, title="Iteration for week 99", velocity=5)
    it99.plan_iteration()

    assert it99.points == it99['velocity']
    assert not it99.slack, "it99 has %d slack remaining!" % it99.slack

    it99.add_story(UserStory(ap, title="Bogus extra story", estimate=3))

