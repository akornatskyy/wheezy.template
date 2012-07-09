
""" Unit tests for ``wheezy.templates.loader``.
"""

import unittest


class FileLoaderTestCase(unittest.TestCase):
    """ Test the ``FileLoader``.
    """

    def setUp(self):
        import os.path
        from wheezy.template.loader import FileLoader
        curdir = os.path.dirname(__file__)
        tmpldir = os.path.join(curdir, 'templates')
        self.loader = FileLoader(directories=[tmpldir])

    def test_list_names(self):
        """ Tests list_names.
        """
        assert (
            'tmpl1.html',
            'shared/master.html',
            'shared/snippet/script.html'
        ) == self.loader.list_names()

    def test_load_existing(self):
        """ Tests load.
        """
        assert '' == self.loader.load('tmpl1.html')

    def test_load_not_found(self):
        """ Tests load if the name is not found.
        """
        assert None == self.loader.load('tmpl-x.html')

    def test_load_not_a_file(self):
        """ Tests load if the name is not a file.
        """
        assert not self.loader.load('shared/snippet')


class DictLoaderTestCase(unittest.TestCase):
    """ Test the ``DictLoader``.
    """

    def setUp(self):
        from wheezy.template.loader import DictLoader
        self.loader = DictLoader(templates={
            'tmpl1.html': 'x',
            'shared/master.html': 'x'
        })

    def test_list_names(self):
        """ Tests list_names.
        """
        assert (
            'tmpl1.html',
            'shared/master.html'
        ) == self.loader.list_names()

    def test_load_existing(self):
        """ Tests load.
        """
        assert 'x' == self.loader.load('tmpl1.html')

    def test_load_not_found(self):
        """ Tests load if the name is not found.
        """
        assert None == self.loader.load('tmpl-x.html')
