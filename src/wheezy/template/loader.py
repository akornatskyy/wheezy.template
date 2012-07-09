
"""
"""

import os
import os.path


class FileLoader(object):

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
        return names

    def get_fullname(self, name):
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
        filename = self.get_fullname(name)
        if filename:
            f = open(filename, 'rb')
            try:
                return f.read().decode(self.encoding)
            finally:
                f.close()
        return None


class DictLoader(object):

    def __init__(self, templates):
        self.templates = templates

    def list_names(self):
        return list(self.templates.keys())

    def load(self, name):
        if name not in self.templates:
            return None
        return self.templates[name]


class ChainLoader(object):

    def __init__(self, loaders):
        self.loaders = loaders

    def load(self, name):
        for loader in self.loaders:
            source = loader.load(name)
            if source:
                return source
        return None


def autoreload(engine, enabled=True):
    if not enabled:
        return engine

    import stat
    from time import time

    class AutoReloadProxy(object):

        def __init__(self, engine):
            self.engine = engine
            self.names = {}

        def __getattr__(self, name):
            return getattr(self.engine, name)

        def get_template(self, name):
            if self.file_changed(name):
                self.remove_name(name)
            return self.engine.get_template(name)

        def render(self, name, ctx, local_defs, super_defs):
            if self.file_changed(name):
                self.remove_name(name)
            return self.engine.render(name, ctx, local_defs, super_defs)

        def import_name(self, name):
            if self.file_changed(name):
                self.remove_name(name)
            return self.engine.import_name(name)

        def remove_name(self, name):
            if name in self.engine.renders:
                del self.engine.templates[name]
                del self.engine.renders[name]
            if name in self.engine.modules:
                del self.engine.modules[name]

        def file_changed(self, name):
            try:
                last_known_stamp = self.names[name]
                current_time = int(time())
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

    return AutoReloadProxy(engine)
