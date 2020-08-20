""" Unit tests for ``wheezy.templates.utils``.
"""

import unittest


class FindAllBalancedTestCase(unittest.TestCase):
    """Test the ``find_all_balanced``."""

    def test_start_out(self):
        """The start index is out of range."""
        from wheezy.template.utils import find_all_balanced

        assert 10 == find_all_balanced("test", 10)

    def test_start_separator(self):
        """If text doesn't start with ``([`` return."""
        from wheezy.template.utils import find_all_balanced

        assert 0 == find_all_balanced("test([", 0)
        assert 3 == find_all_balanced("test([", 3)

    def test_not_balanced(self):
        """Separators are not balanced."""
        from wheezy.template.utils import find_all_balanced

        assert 4 == find_all_balanced("test(a, b", 4)
        assert 4 == find_all_balanced("test[a, b()", 4)

    def test_balanced(self):
        """Separators are balanced."""
        from wheezy.template.utils import find_all_balanced

        assert 10 == find_all_balanced("test(a, b)", 4)
        assert 13 == find_all_balanced("test(a, b)[0]", 4)
        assert 12 == find_all_balanced("test(a, b())", 4)
        assert 17 == find_all_balanced("test(a, b())[0]()", 4)


class FindBalancedTestCase(unittest.TestCase):
    """Test the ``find_balanced``."""

    def test_start_out(self):
        """The start index is out of range."""
        from wheezy.template.utils import find_balanced

        assert 10 == find_balanced("test", 10)

    def test_start_separator(self):
        """If text doesn't start with ``start_sep`` return."""
        from wheezy.template.utils import find_balanced

        assert 0 == find_balanced("test(", 0)
        assert 3 == find_balanced("test(", 3)

    def test_not_balanced(self):
        """Separators are not balanced."""
        from wheezy.template.utils import find_balanced

        assert 4 == find_balanced("test(a, b", 4)
        assert 4 == find_balanced("test(a, b()", 4)

    def test_balanced(self):
        """Separators are balanced."""
        from wheezy.template.utils import find_balanced

        assert 10 == find_balanced("test(a, b)", 4)
        assert 12 == find_balanced("test(a, b())", 4)
