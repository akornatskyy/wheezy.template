
"""
"""

import os
import os.path
import stat
import time


class FileLoader(object):
    """ Loads templates from file system.

        ``directories`` - search path of directories to scan for template.
        ``encoding`` - decode template content per encoding.
    """

    def __init__(self, directories, encoding='UTF-8'):
        searchpath = []
        for path in directories:
            abspath = os.path.abspath(path)
            assert os.path.exists(abspath)
            assert os.path.isdir(abspath)
            searchpath.append(abspath)
        self.searchpath = searchpath
        self.encoding = encoding

    def list_names(self):
        """ Return a list of names relative to directories. Ignores any files
            and directories that start with dot.
        """
        names = []
        for path in self.searchpath:
            pathlen = len(path) + 1
            for dirpath, dirnames, filenames in os.walk(path):
                for i in [i for i, name in enumerate(dirnames)
                          if name.startswith('.')]:
                    del dirnames[i]
                for filename in filenames:
                    if filename.startswith('.'):
                        continue
                    name = os.path.join(dirpath, filename)[pathlen:]
                    name = name.replace('\\', '/')
                    names.append(name)
        return tuple(sorted(names))

    def get_fullname(self, name):
        """ Returns a full path by a template name.
        """
        for path in self.searchpath:
            filename = os.path.join(path, name)
            if not os.path.exists(filename):
                continue
            if not os.path.isfile(filename):
                continue
            return filename
        else:
            None

    def load(self, name):
        """ Loads a template by name from file system.
        """
        filename = self.get_fullname(name)
        if filename:
            f = open(filename, 'rb')
            try:
                return f.read().decode(self.encoding)
            finally:
                f.close()
        return None


class DictLoader(object):
    """ Loads templates from python dictionary.

        ``templates`` - a dict where key corresponds to template name and
        value to template content.
    """

    def __init__(self, templates):
        self.templates = templates

    def list_names(self):
        """ List all keys from internal dict.
        """
        return tuple(sorted(self.templates.keys()))

    def load(self, name):
        """ Returns template by name.
        """
        if name not in self.templates:
            return None
        return self.templates[name]


class ChainLoader(object):
    """ Loads templates from ``loaders`` until first succeed.
    """

    def __init__(self, loaders):
        self.loaders = loaders

    def list_names(self):
        """ Returns as list of names from all loaders.
        """
        names = set()
        for loader in self.loaders:
            names |= set(loader.list_names())
        return tuple(sorted(names))

    def load(self, name):
        """ Returns template by name from the first loader that succeed.
        """
        for loader in self.loaders:
            source = loader.load(name)
            if source is not None:
                return source
        return None


class PreprocessLoader(object):
    """ Performs preprocessing of loaded template.
    """

    def __init__(self, engine, ctx=None):
        self.engine = engine
        self.ctx = ctx or {}

    def list_names(self):
        return self.engine.loader.list_names()

    def load(self, name):
        return self.engine.render(name, self.ctx, {}, {})


def autoreload(engine, enabled=True):
    """ Auto reload template if changes are detected in file.

        Limitation: master (inherited), imported and preprocessed templates.

        It is recommended to use application server that supports
        file reload instead.
    """
    if not enabled:
        return engine
    return AutoReloadProxy(engine)


# region: internal details

class AutoReloadProxy(object):

    def __init__(self, engine):
        from warnings import warn
        self.engine = engine
        self.names = {}
        warn('autoreload limitation: master (inherited), imported '
             'and preprocessed templates. It is recommended to use '
             'application server that supports file reload instead.',
             stacklevel=3)

    def get_template(self, name):
        if self.file_changed(name):
            self.remove(name)
        return self.engine.get_template(name)

    def render(self, name, ctx, local_defs, super_defs):
        if self.file_changed(name):
            self.remove(name)
        return self.engine.render(name, ctx, local_defs, super_defs)

    def remove(self, name):
        self.engine.remove(name)

    # region: internal details

    def __getattr__(self, name):
        return getattr(self.engine, name)

    def file_changed(self, name):
        try:
            last_known_stamp = self.names[name]
            current_time = int(time.time())
            if current_time - last_known_stamp <= 2:
                return False
        except KeyError:
            last_known_stamp = 0

        abspath = self.engine.loader.get_fullname(name)
        if not abspath:
            return False

        last_modified_stamp = os.stat(abspath)[stat.ST_MTIME]
        if last_modified_stamp <= last_known_stamp:
            return False
        self.names[name] = last_modified_stamp
        return True
