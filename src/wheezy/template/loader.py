
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
                for filename in filenames:
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


def uwsgi_autoreload(loader, signum=0, enabled=True):  # pragma: nocover
    if enabled:
        try:
            import uwsgi
        except ImportError:
            pass
        else:
            if uwsgi.masterpid() == 0:
                from warnings import warn
                warn('uwsgi_autoreload: '
                     'You have to enable the uwsgi master process',
                     stacklevel=2)
            else:
                if not uwsgi.signal_registered(signum):
                    uwsgi.register_signal(signum, '', uwsgi.reload)
                    for name in loader.list_names():
                        fullname = loader.get_fullname(name)
                        uwsgi.add_file_monitor(signum, fullname)
    return loader
