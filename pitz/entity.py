# vim: set expandtab ts=4 sw=4 filetype=python:

from copy import copy
import logging
from datetime import datetime
import os, uuid, warnings

import yaml

import jinja2

from pitz.exceptions import NoProject

logging.basicConfig(level=logging.INFO)

class Entity(dict):
    """
    Acts like a regular dictionary with a few extra tweaks.
    """

    required_fields = dict(title='no title')
    pointers = list()
    allowed_values = dict()

    def __init__(self, project=None, **kwargs):

        # Now make sure we got all the required fields.
        for rf, default_value in self.required_fields.items():

            if rf not in kwargs:

                # Use a default value if we got one.  
                if default_value:
                    kwargs[rf] = default_value

                # Otherwise, raise an exception.
                else:
                    raise ValueError("I need a value for %s!" % rf)

        self.update(**kwargs)
        self['type'] = self.__class__.__name__.lower()

        # Make a unique name if we didn't get one.
        if 'name' not in kwargs:
            self['name'] = str(uuid.uuid4())

        self['frag'] = self['name'][:6]

        # Handle attributes with defaults.
        if 'created_time' not in kwargs:
            self['created_time'] = datetime.now() 

        if 'modified_time' not in kwargs:
            self['modified_time'] = self['created_time']

        # Add this entity to the project (if we got a project).
        self.project = project
        if project is not None:
            self.project.append(self)

    def __setitem__(self, attr, val):
        """
        Make sure that the value is allowed for this attr before going
        any further.
        """

        if attr in self.allowed_values and val not in self.allowed_values[attr]:
            raise ValueError("%s must be in %s, not %s!" 
                % (attr, self.allowed_values[attr], val))

        else:
            super(Entity, self).__setitem__(attr, val)

    @property
    def frag(self):
        return self['frag']

    @property
    def name(self):
        return self['name']

    def matches_dict(self, **d):
        """
        Just like self.matches_pairs, except accepts keyword args.

        >>> e = Entity(title='Clean cat box', creator='Matt')
        >>> e.matches_dict(creator='Matt') == e
        True
        >>> e.matches_dict(creator='Nobody') == None
        True
        """

        for a, v in d.items():

            if a not in self or self[a] != v:
                return

        return self

    def does_not_match_dict(self, **d):
        """
        Returns self if ALL of the key-value pairs do not match.

        >>> e = Entity(title="blah", a=1, b=2)
        >>> e.does_not_match_dict(a=99, b=99, c=99) == e
        True
        >>> e.does_not_match_dict(a=1, b=1) == None
        True
        >>> e.does_not_match_dict(a=1) == None
        True
        >>> e.does_not_match_dict(c=1) == e
        True
        """

        for a, v in d.items():

            if a in self and self[a] == v:
                return

        return self

    def __repr__(self):
        return "<pitz.%s %s>" \
        % (self.__class__.__name__, self.summarized_view)

    @property
    def frag(self):
        return self['name'][:12]

    @property
    def summarized_view(self):
        """
        Short description of the entity.
        """

        return "%(frag)s: %(title)s" % self

    @property
    def detailed_view(self):
        """
        The detailed view of the entity.
        """

        d = dict()
        d.update(self)
        d['summarized_view'] = self.summarized_view
        d['line_of_dashes'] = "-" * len(self.summarized_view)
        d['type'] = self.__class__.__name__
        d['data'] = self

        t = jinja2.Template("""\
{{summarized_view}}
{{line_of_dashes}}

{% for k in data %}
{{ k }}:
{% if hasattr(data[k], 'summarized_view') -%} 
{{ data[k].summarized_view -}}
{% else -%} 
{{ data[k] -}}
{% endif %}
{% endfor %}
""")

        return t.render(hasattr=hasattr, **d)


    def __str__(self):
        return self.detailed_view

    @property
    def yaml(self):

        self.replace_objects_with_pointers()

        d = dict(self)
        d.pop('frag')

        y = yaml.dump(d, default_flow_style=False)

        # Now switch the pointers with the objects.
        if self.project:
            self.replace_pointers_with_objects()

        return y

    def to_yaml_file(self, pathname):
        """
        Returns the path of the file saved.

        The pathname specifies where to save it.
        """

        fp = os.path.join(pathname, '%(type)s-%(name)s.yaml' % self)
        f = open(fp, 'w')
        f.write(self.yaml)
        f.close()
        logging.debug("Saved file %s" % fp)

        return fp

    def replace_pointers_with_objects(self):

        """
        Replace pointer to entities with the entities that are pointed
        to.

        In other words, replaces the string "matt" with the object with
        "matt" as its name.
        """

        if self.project:
            for ptr in self.pointers:
                if ptr in self:
                    self[ptr] = self.project.by_name(self[ptr])


    def replace_objects_with_pointers(self):
        """
        Replaces the value of an entity with just the string of the
        entity's name.

        In other words, replaces the object stored at sef['creator']
        with just the name of that object.
        """

        for ptr in self.pointers:
            if ptr in self:
                o = self[ptr]

                # Remember that all subclasses of Entity will return
                # True for isinstance(o, Entity).
                if isinstance(o, Entity):
                    self[ptr] = o.name

    @classmethod
    def from_yaml_file(cls, fp, project=None):
        """
        Loads the file at file path fp into the project and returns it.
        """

        d = yaml.load(open(fp))

        if not d:
            return

        e = cls(project, **d)

        return e
