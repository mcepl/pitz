# vim: set expandtab ts=4 sw=4 filetype=python:

import glob, os

import yaml

from clepy import walkup

from pitz.bag import Bag
from pitz.entity import Entity
from pitz import *

class Project(Bag):

    """
    The project is the bag that everybody should track, because it is
    the only thing that keeps references to every other thing.
    """

    # These are all the classes that I will try to instantiate when
    # reading yaml files.
    classes = dict(
        entity = Entity
    )


    def __init__(self, title='', uuid=None, pathname=None, entities=(), 
        order_method=by_created_time, load_yaml_files=True, **kwargs):

        super(Project, self).__init__(title, uuid, pathname, entities,
            order_method, **kwargs)

        self.rerun_sort_after_append = True

        # Only load from the file system if we don't have anything.
        if self.pathname and load_yaml_files and not entities:
            self.load_entities_from_yaml_files()

        # Tell all the entities to replace their pointers with objects.
        self.replace_pointers_with_objects()


    def append(self, e):
        """
        Do a regular append and some other stuff too.
        """

        super(Project, self).append(e, self.rerun_sort_after_append)

        # Make sure the entity remembers this project.
        e.project = self


    def load_entities_from_yaml_files(self, pathname=None):
        """
        Loads all the files matching pathglob into this project.
        """

        if pathname:
            self.pathname = pathname

        if not self.pathname:
            raise ValueError("I need a path to the files!")

        if not os.path.isdir(self.pathname):
            raise ValueError("%s isn't a directory." % self.pathname)

        pathglob = os.path.join(self.pathname, '*.yaml')

        self.rerun_sort_after_append = False
        for fp in glob.glob(pathglob):

            bn = os.path.basename(fp)

            # Skip the project yaml file.
            if bn == 'project.yaml' \
            or bn.startswith(self.__class__.__name__.lower()):

                continue

            # Extract the class name and then look it up
            classname, dash, remainder = bn.partition('-')
            C = self.classes[classname]
            C.from_yaml_file(fp, self)

        self.rerun_sort_after_append = True
        return self


    def save_entities_to_yaml_files(self, pathname=None):
        """
        Tell every entity to write itself out to YAML.
        """

        if pathname is None and self.pathname is None:
            raise ValueError("I need a pathname!")

        if self.pathname is None and pathname is not None:
            self.pathname = pathname

        if not os.path.isdir(self.pathname):
            raise ValueError("%s is not a directory!")

        pathname = pathname or self.pathname

        # Send all the entities to the filesystem.
        return [e for e in self if e.to_yaml_file(self.pathname)]


    @property
    def yaml(self):
        """
        Return a block of yaml.
        """

        data = dict(
            module=self.__module__,
            classname=self.__class__.__name__,
            title=self.title,
            order_method_name=self.order_method.func_name,
            uuid=self.uuid,
        )

        return yaml.dump(data, default_flow_style=False)


    def to_yaml_file(self, pathname=None):
        """
        Save this project to a YAML file.
        """

        if not pathname \
        and (self.pathname is None or not os.path.isdir(self.pathname)):

            raise ValueError("I need a pathname!")

        pathname = pathname or self.pathname
        lowered_class_name = self.__class__.__name__.lower()
        uuid = self.uuid

        fp = os.path.join(pathname, 'project.yaml')

        f = open(fp, 'w')
        f.write(self.yaml)
        f.close()

        return fp


    @classmethod
    def find_yaml_file(cls, filename='project.yaml', walkdown=False):
        """
        Raise an exception or return the path to the project.yaml file.

        Check the os.environ first and then walk up the filesystem, then
        walk down the filesystem IFF walkdown is True.

        By the way, walking down can take a REALLY long time if you're
        at the top of a big file system.
        """

        yamlpath = os.path.join(os.environ.get('PITZDIR', ''), 'project.yaml')

        if os.path.isfile(yamlpath):
            return yamlpath
        
        starting_path = os.getcwd()

        # Walk up...
        for dir in walkup(starting_path):

            a = os.path.join(dir, 'pitzdir', filename)

            if os.path.isfile(a):
                return a

        # Walk down...
        if walkdown:
            for root, dirs, files in os.walk(starting_path):

                if 'pitzdir' in dirs:
                    a = os.path.join(dir, 'pitzdir', filename)

                if os.path.isfile(a):
                    return a

        raise ProjectYamlNotFound("Started looking at %s" % starting_path)

    @property
    def html_filename(self):

        return "index.html"

    @classmethod
    def from_yaml_file(cls, fp):
        """
        Instantiate the class based on the data in file fp.

        IMPORTANT: this may not return an instance of this project.
        Instead it will return an instance of the project subclass
        specified in the yaml data.
        """

        yamldata = yaml.load(open(fp))

        # Read the section on __import__ at
        # http://docs.python.org/library/functions.html
        # to make sense out of this.
        m = __import__(yamldata['module'],
            fromlist=yamldata['classname'])

        yamldata['pathname'] = os.path.realpath(os.path.dirname(fp))

        # Dig out the string that points to the order method and replace
        # it with the actual function.  This is really ugly, so feel
        # free to fix it.
        yamldata['order_method'] = globals()[yamldata['order_method_name']]
        yamldata.pop('order_method_name')

        # This big P is the class of the project.
        P = getattr(m, yamldata['classname'])

        return P(**yamldata)
