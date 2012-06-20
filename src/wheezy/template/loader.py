
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

    def load(self, name):
        for path in self.searchpath:
            filename = os.path.join(path, name)
            if not os.path.exists(filename):
                continue
            if not os.path.isfile(filename):
                continue
            f = open(filename, 'rb')
            try:
                return f.read().decode(self.encoding)
            finally:
                f.close()
        else:
            return None
