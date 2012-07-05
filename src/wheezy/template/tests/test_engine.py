
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
        self.assertRaises(IOError, lambda: self.engine.render(
            'x', {}, {}, {}))

    def test_import_not_found(self):
        """ Raises IOError.
        """
        self.assertRaises(IOError, lambda: self.engine.import_name(
            'x', {}))
