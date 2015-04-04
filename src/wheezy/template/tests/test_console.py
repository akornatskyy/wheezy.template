
""" Unit tests for ``wheezy.templates.console``.
"""

import unittest

from wheezy.template.console import json


class Console(object):
    """ Test the console ``main`` function.
    """

    def test_usage(self):
        assert 2 == main(['-h'])
        assert 2 == main(['-t @'])
        assert 2 == main(['-x'])

    def test_context_file(self):
        assert 0 == main(['demos/helloworld/hello.txt',
                          'demos/helloworld/hello.json'])

    def test_context_string(self):
        assert 0 == main(['demos/helloworld/hello.txt', '{"name": "World"}'])

    def test_master(self):
        assert 0 == main(['-s', 'demos/master', 'index.html'])


if json:
    from wheezy.template.console import main

    class ConsoleTestCase(unittest.TestCase, Console):
        """ Test the console ``main`` function.
        """
        pass
