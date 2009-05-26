# vim: set expandtab ts=4 sw=4 filetype=python:

"""
Verify the stuff in simplepitz works.
"""

from nose.tools import raises, with_setup

from pitz.exceptions import NoProject
from pitz.projecttypes.simplepitz import *

p = None

def setup():

    global p
    p = SimpleProject()
    p.append(Task(title='Draw new accounting report', priority=2))
    p.append(Task(title='Improve speed of search page', priority=0))

    p.append(Task(title='Add animation to site logo',
        estimate=2))

    p.append(Task(title='Write "forgot password?" feature',
        priority=1, estimate=2))

    p.append(Task(title='Allow customer to change contact information',
        priority=2, estimate=2))

    p.append(Task(title='Allow customer to change display name',
        priority=2, estimate=1))

    p.append(Milestone(title="1.0"))
    p.append(Milestone(title="2.0"))

@raises(NoProject)
def test_noproject():
    m = Milestone()
    m.tasks

def test_show_milestones():
    """
    List every milestone.
    """

    global p

    for m in p.milestones:
        m.todo
    
def test_milestone_todo():
    
    global p

    for m in p.milestones:
        m.todo

def test_comments():

    global p
    t = Task(p, title="wash dishes")
    z = Comment(p, entity=t, text="I don't want to!", who_said_it="Matt")
    c = t.comments[0]
    c.summarized_view

def test_project_todo():

    global p
    p.todo


def test_project_tasks():

    global p
    p.tasks

def test_project_people():

    global p
    p.people

def test_project_comments():

    global p
    p.comments

def test_unscheduled():

    global p
    p.unscheduled