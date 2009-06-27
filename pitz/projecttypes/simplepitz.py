# vim: set expandtab ts=4 sw=4 filetype=python:

"""
Simple projects have tasks, people, comments, components, and
milestones.
"""

myclassname = 'SimpleProject'

from copy import copy
import logging, textwrap

import jinja2

from pitz import *
from pitz.entity import Entity
from pitz.project import Project
from pitz.exceptions import NoProject

log = logging.getLogger('pitz.simplepitz')

class Milestone(Entity):
    """
    Useful for bundling tasks
    """

    plural_name = "milestones"

    @property
    def tasks(self):

        if not self.project:
            raise NoProject("I need a project before I can look up tasks!")

        tasks = self.project(type='task', milestone=self)
        tasks.title = 'Tasks in %(title)s' % self
        return tasks

    @property
    def todo(self):

        unfinished = self.tasks.does_not_match_dict(status='finished')\
        .does_not_match_dict(status='abandoned')

        unfinished.title = "Unfinished tasks in %(title)s" % self
        return unfinished

    @property
    def summarized_view(self):

        a = self.tasks(status='finished').length
        b = self.tasks.length

        if b is not 0:
            pct_complete = 100*(float(a)/b)
        else:
            pct_complete = 0.0

        d = {
            'title':self['title'],
            'pct_complete':pct_complete,
            'num_finished_tasks':a,
            'num_tasks': b}
            
        s = "%(title)s: %(pct_complete)0.0f%% complete (%(num_finished_tasks)d / %(num_tasks)d tasks)"
        return s % d


class Task(Entity):

    plural_name = "tasks"

    required_fields = dict(
        milestone='unscheduled',
        title='no title',
        status='unstarted')

    allowed_values = dict(
        status=['unstarted', 'started', 'abandoned', 'finished'],
    )


    @property
    def summarized_view(self):
        """
        Short description of the task.
        """

        return "%(frag)s %(title)s (%(status)s)" % self

    @property
    def comments(self):
        """
        Return all comments on this task.
        """
    
        b = self.project(type='comment', entity=self)
        b.title = 'Comments on %(title)s' % self
        return b.order(by_created_time)


    def abandon(self):

        if self['status'] in ['unstarted', 'started']:
            self['status'] = 'abandoned'
            return self

        else:
            raise ValueError('You can only abandon unstarted or started tasks.')


    def start(self):

        if self['status'] in ['unstarted', 'abandoned']:
            self['status'] = 'started'
            return self

        else:
            raise ValueError('You can only start unstarted or abandoned tasks.')


    def finish(self):

        if self['status'] == 'started':
            self['status'] = 'finished'
            return self

        else:
            raise ValueError('You can only finish started.')


class Comment(Entity):

    """
    You can comment on any entity.
    """

    plural_name = "comments"
    
    required_fields = dict(
        who_said_it=None,
        text=None,
        entity=None,
        title='no title')

    @property
    def summarized_view(self):

        text = self['text'].strip().replace('\n', ' ')
        text = "%s..." % text[:60] if len(text) > 60 else text

        who_said_it = self['who_said_it']
        who_said_it = getattr(who_said_it, 'title', who_said_it)
        
        return "%(who_said_it)s said: %(text)s" % dict(
            who_said_it=who_said_it,
            time=self['created_time'].strftime("%I:%M %P, %a, %m/%d/%y"),
            text=text,
        )


    @property
    def detailed_view(self):

        text = textwrap.fill(self['text'].strip().replace('\n', '  '))

        who_said_it = self['who_said_it']
        who_said_it = getattr(who_said_it, 'title', who_said_it)

        time = self['created_time'].strftime("%A, %B %d, %Y, at %I:%M %P")
        
        tmpl = jinja2.Template("""\
{{who_said_it}} on {{time}} said:

{{text}}
""")

        return tmpl.render(locals())


class Person(Entity):
    """
    Maybe you want to track who is doing what.
    """

    plural_name = "people"


class Component(Entity):

    plural_name = "component"

    @property
    def tasks(self):

        if not self.project:
            raise NoProject("I need a project before I can look up tasks!")

        tasks = self.project(type='task', milestone=self)
        tasks.title = 'Tasks in %(title)s' % self
        return tasks

    @property
    def todo(self):

        unfinished = self.tasks.does_not_match_dict(status='finished')\
        .does_not_match_dict(status='abandoned')

        unfinished.title = "Unfinished tasks in %(title)s" % self
        return unfinished
    

class SimpleProject(Project):
    """
    Just like the regular project, but with some queries as properties.
    """

    # These are all the classes I deal with.
    classes = dict(
        task=Task,
        person=Person,
        milestone=Milestone,
        comment=Comment,
        component=Component)

    @property
    def todo(self):

        b = self(type='task')\
        .does_not_match_dict(status='finished')\
        .does_not_match_dict(status='abandoned')

        b.title = '%s: stuff to do' % self.title
        return b

    # TODO: replace all this with some metaclass tomfoolery.
    @property
    def milestones(self):
        b = self(type='milestone')
        b.title = 'Milestones'
        return b

    @property
    def components(self):
        b = self(type='component')
        b.title = 'Components'
        return b

    @property
    def tasks(self):
        b = self(type='task')
        b.title = 'Tasks'
        return b
        
    @property
    def people(self):
        b = self(type='person')
        b.title = 'People'
        return b

    @property
    def comments(self):
        b = self(type='comment')
        b.title = 'Comments'
        return b

    @property
    def unscheduled(self):
        """
        Unfinished tasks not linked to any milestones.
        """

        b = self(type='task').does_not_match_dict(status='finished')

        for m in self.milestones:
            b = b.does_not_match_dict(milestone=m)

        b.title = 'Unscheduled and unfinished tasks'
        return b


    @property
    def started(self):
        b = self(type='task', status='started')
        b.title = 'Started tasks'
        return b
