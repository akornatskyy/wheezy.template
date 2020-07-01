""" Unit tests for ``wheezy.templates.ext.determined``.
"""

import unittest


class DeterminedTestCase(unittest.TestCase):
    """ Test the ``DeterminedExtension``.
    """

    def setUp(self):
        from wheezy.template.ext.determined import DeterminedExtension

        self.preprocess = DeterminedExtension(
            known_calls=["path_for", "_"]
        ).preprocessors[0]

    def test_determined(self):
        """ Substitute determinded expressions for known calls to
            preprocessor calls.
        """
        assert """\
            #ctx['_']('Name:')
            #ctx['path_for']('default')
            #ctx['path_for']('static', path='/static/css/site.css')
        """ == self.preprocess(
            """\
            @_('Name:')
            @path_for('default')
            @path_for('static', path='/static/css/site.css')
        """
        )

    def test_undetermined(self):
        """ Calls that are not determined left unchanged.
        """
        assert """\
            @path_for('item', id=id)
            @model.username.label(_('Username: '))
        """ == self.preprocess(
            """\
            @path_for('item', id=id)
            @model.username.label(_('Username: '))
        """
        )
