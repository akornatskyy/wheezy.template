""" Unit tests for ``wheezy.templates.builder``.
"""

import unittest


class BlockBuilderTestCase(unittest.TestCase):
    """ Test the ``BlockBuilder`` blocks.
    """

    def setUp(self):
        from wheezy.template.builder import BlockBuilder

        self.builder = BlockBuilder([])

    def test_start_end_block(self):
        """ Test start_block and end_block.
        """
        self.builder.start_block()
        assert self.builder.indent == "    "
        self.builder.end_block()
        assert self.builder.indent == ""

    def test_unexpected_end_block(self):
        """ Test raises error.
        """
        self.assertRaises(SyntaxError, lambda: self.builder.end_block())

    def test_inconsistence(self):
        """ Test add a line with wrong lineno.
        """
        self.assertRaises(SyntaxError, lambda: self.builder.add(-1, ""))

    def test_unknown_token(self):
        """ Test raises error if token is unknown.
        """
        self.assertRaises(
            SyntaxError, lambda: self.builder.build_token(1, "x", None)
        )


class BlockBuilderAddSameLineTestCase(unittest.TestCase):
    """ Test the ``BlockBuilder.add`` to the same line.
    """

    def setUp(self):
        from wheezy.template.builder import BlockBuilder

        self.builder = BlockBuilder([], indent="    ", lineno=1)

    def test_code_empty(self):
        self.builder.buf = [""]
        self.builder.add(1, "")
        assert "" == self.builder.to_string()

    def test_line_empty(self):
        self.builder.buf = [""]
        self.builder.add(1, "pass")
        assert "    pass" == self.builder.to_string()

    def test_line_ends_colon(self):
        self.builder.buf = ["def title():"]
        self.builder.add(1, 'return ""')
        assert 'def title():return ""' == self.builder.to_string()

    def test_continue_same_line(self):
        self.builder.buf = ["pass"]
        self.builder.add(1, "pass")
        assert "pass; pass" == self.builder.to_string()


class BlockBuilderAddNextLineTestCase(unittest.TestCase):
    """ Test the ``BlockBuilder.add`` to add a new line.
    """

    def setUp(self):
        from wheezy.template.builder import BlockBuilder

        self.builder = BlockBuilder([], indent="    ")

    def test_code_empty(self):
        self.builder.add(1, "pass")
        self.builder.add(2, "")
        assert "    pass\n" == self.builder.to_string()

    def test_pad(self):
        self.builder.add(1, "pass")
        self.builder.add(3, "pass")
        assert "    pass\n\n    pass" == self.builder.to_string()
