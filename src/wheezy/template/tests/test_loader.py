
""" Unit tests for ``wheezy.templates.loader``.
"""

import unittest

from mock import Mock
from mock import patch


class FileLoaderTestCase(unittest.TestCase):
    """ Test the ``FileLoader``.
    """

    def setUp(self):
        import os.path
        from wheezy.template.loader import FileLoader
        self.tmpldir = os.path.dirname(__file__)
        self.loader = FileLoader(directories=[self.tmpldir])

    @patch('os.walk')
    def test_get_template(self, mock_walk):
        mock_walk.return_value = [
            (self.tmpldir + '/',
             ['.ignore', 'shared'],
             ['.ignore', 'tmpl1.html']),
            (self.tmpldir + '/shared',
             ['.ignore', 'snippet'],
             ['master.html', '.ignore']),
            (self.tmpldir + '/shared/snippet',
             ['.ignore'],
             ['.ignore', 'script.html'])
        ]
        assert (
            'shared/master.html',
            'shared/snippet/script.html',
            'tmpl1.html'
        ) == self.loader.list_names()

    def test_load_existing(self):
        """ Tests load.
        """
        assert '' == self.loader.load('__init__.py')

    def test_load_not_found(self):
        """ Tests load if the name is not found.
        """
        assert not self.loader.load('tmpl-x.html')

    def test_load_not_a_file(self):
        """ Tests load if the name is not a file.
        """
        assert not self.loader.load('..')


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
            'shared/master.html',
            'tmpl1.html'
        ) == self.loader.list_names()

    def test_load_existing(self):
        """ Tests load.
        """
        assert 'x' == self.loader.load('tmpl1.html')

    def test_load_not_found(self):
        """ Tests load if the name is not found.
        """
        assert None == self.loader.load('tmpl-x.html')


class ChainLoaderTestCase(unittest.TestCase):
    """ Test the ``ChainLoader``.
    """

    def setUp(self):
        from wheezy.template.loader import ChainLoader
        from wheezy.template.loader import DictLoader
        self.loader = ChainLoader(loaders=[
            DictLoader(templates={
                'tmpl1.html': 'x1',
            }),
            DictLoader(templates={
                'shared/master.html': 'x2'
            })])

    def test_list_names(self):
        """ Tests list_names.
        """
        assert (
            'shared/master.html',
            'tmpl1.html'
        ) == self.loader.list_names()

    def test_load_existing(self):
        """ Tests load.
        """
        assert 'x1' == self.loader.load('tmpl1.html')
        assert 'x2' == self.loader.load('shared/master.html')

    def test_load_missing(self):
        """ Tests load not found.
        """
        assert not self.loader.load('missing')


class PreprocessLoaderTestCase(unittest.TestCase):
    """ Test the ``PreprocessLoader``.
    """

    def setUp(self):
        from wheezy.template.loader import PreprocessLoader
        from wheezy.template.loader import DictLoader

        class Engine(object):

            def render(self, name, ctx, d1, d2):
                assert {'x': 1} == ctx
                return 'x'

        engine = Engine()
        engine.loader = DictLoader(templates={
            'tmpl1.html': 'x1',
            'shared/master.html': 'x2'
        })
        self.loader = PreprocessLoader(engine, {'x': 1})

    def test_list_names(self):
        """ Tests list_names.
        """
        assert (
            'shared/master.html',
            'tmpl1.html'
        ) == self.loader.list_names()

    def test_load_existing(self):
        """ Tests load existing.
        """
        assert 'x' == self.loader.load('tmpl1.html')


class AutoReloadProxyTestCase(unittest.TestCase):
    """ Test the ``PreprocessLoader``.
    """

    def setUp(self):
        import warnings
        from wheezy.template.loader import autoreload
        self.mock_engine = Mock()
        self.mock_engine.loader.get_fullname.return_value = '/t.html'
        self.mock_engine.get_template.return_value = 't'
        self.mock_engine.render.return_value = 'x'
        warnings.simplefilter('ignore')
        self.proxy = autoreload(self.mock_engine)
        warnings.simplefilter('default')

    def test_disabled(self):
        """ Tests autoreload disabled.
        """
        from wheezy.template.loader import autoreload
        assert None == autoreload(None, enabled=False)

    @patch('os.stat')
    def test_get_template(self, mock_stat):
        """ Tests get_template.
        """
        import stat
        mock_stat.return_value.__getitem__.return_value = 777
        assert 't' == self.proxy.get_template('t.html')
        self.mock_engine.loader.get_fullname.assert_called_once_with('t.html')
        mock_stat.assert_called_once_with('/t.html')
        mock_stat.return_value.__getitem__.assert_called_once_with(
            stat.ST_MTIME)
        assert 777 == self.proxy.names['t.html']

    @patch('os.stat')
    def test_render(self, mock_stat):
        """ Tests render.
        """
        mock_stat.return_value.__getitem__.return_value = 777
        ctx = {1: 1}
        local_defs = {2: 2}
        super_defs = {3: 3}
        assert 'x' == self.proxy.render('t.html', ctx, local_defs, super_defs)

    def test_getattr(self):
        """ Tests __getattr__.
        """
        self.mock_engine.x = 100
        assert 100 == self.proxy.x

    def test_file_not_found(self):
        """ Tests file not found.
        """
        self.mock_engine.loader.get_fullname.return_value = None
        assert not self.proxy.file_changed('t.html')
        self.mock_engine.loader.get_fullname.assert_called_once_with('t.html')

    def test_file_not_changed_first_access(self):
        """ Tests not changed on first access.
        """
        from time import time
        self.proxy.names['t.html'] = int(time())
        assert not self.proxy.file_changed('t.html')

    @patch('os.stat')
    def test_file_not_changed_known(self, mock_stat):
        """ Test not changed for the file that was previously accessed.
        """
        self.proxy.names['t.html'] = 777
        mock_stat.return_value.__getitem__.return_value = 777
        assert not self.proxy.file_changed('t.html')
