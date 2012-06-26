
""" Unit tests for ``wheezy.templates.ext.core``.
"""

import unittest


class CleanSourceTestCase(unittest.TestCase):
    """ Test the ``clean_source``.
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
