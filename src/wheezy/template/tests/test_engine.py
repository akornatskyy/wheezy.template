
""" Unit tests for ``wheezy.templates.engine.Engine``.
"""

import unittest


class EngineTestCase(unittest.TestCase):
    """ Test the ``Engine``.
    """

    def setUp(self):
        from wheezy.template.engine import Engine
        from wheezy.template.loader import DictLoader
        self.engine = Engine(
            loader=DictLoader(templates={}),
            extensions=[])

    def test_template_not_found(self):
        """ Raises IOError.
        """
        self.assertRaises(IOError, lambda: self.engine.get_template('x'))

    def test_import_not_found(self):
        """ Raises IOError.
        """
        self.assertRaises(IOError, lambda: self.engine.import_name('x'))

    def test_remove_unknown_name(self):
        """ Invalidate name that is not known to engine.
        """
        self.engine.remove('x')

    def test_remove_name(self):
        """ Invalidate name that is known to engine.
        """
        self.engine.templates['x'] = 'x'
        self.engine.renders['x'] = 'x'
        self.engine.modules['x'] = 'x'
        self.engine.remove('x')
