
User Guide
==========

:ref:`wheezy.template` uses :py:class:`~wheezy.template.engine.Engine` to store
configuration information and load templates. Here is a typical example that
loads templates from the file system::

    from wheezy.template.engine import Engine
    from wheezy.template.ext.core import CoreExtension
    from wheezy.template.loader import FileLoader

    searchpath = ['content/templates-wheezy']
    engine = Engine(
        loader=FileLoader(searchpath),
        extensions=[CoreExtension()]
    )
    template = engine.get_template('template.html')

Loaders
-------

Loader is used to provide template content to :py:class:`~wheezy.template.engine.Engine`
by some name requested by an application. What exactly consitutes a name and how each loader
interprets it, is up to the loader implementation.

:ref:`wheezy.template` comes with the following loaders:

* :py:class:`~wheezy.template.loader.FileLoader` - loads templates from file
  system (``directories`` - search path of directories to scan for template,
  ``encoding`` - template content encoding).
* :py:class:`~wheezy.template.loader.DictLoader` - loads templates from python
  dictionary (``templates`` - a dict where key corresponds to template name
  and value to template content).
* :py:class:`~wheezy.template.loader.ChainLoader` - loads templates from
  ``loaders`` in turn until one succeeds.

Core Extension
--------------

The :py:class:`~wheezy.template.ext.core.CoreExtension` includes support for
basic python statements, variables processing and markup.

Context
~~~~~~~

In order to use variables passed to a template you use ``require`` statement and
list names you need to pick from the context. These names becomes
visible from the ``require`` statement to the
end of the template scope (imagine a single template is a python function).

Context access syntax::

    @require(var1, var2, ...)

Variables
~~~~~~~~~

The application passes variables to the template renderer via context.
Variable access syntax::

    @variable_name
    @{variable_name}
    @{ variable_name }

Example::

    from wheezy.template.engine import Engine
    from wheezy.template.ext.core import CoreExtension
    from wheezy.template.loader import DictLoader

    template = """\
    @require(name)
    Hello, @name"""

    engine = Engine(
        loader=DictLoader({'x': template}),
        extensions=[CoreExtension()]
    )
    template = engine.get_template('x')

    print(template.render({'name': 'John'}))

Variable syntax is not limited to a single name access. You are able to use
full power of python to access items in a dict, attributes, function calls, etc.

Filters
~~~~~~~

Variables can be formatted by filters. Filters are separated from the variable
by the ``!`` symbol. Filter syntax::

    @variable_name!filter1!filter2
    @{variable_name!!filter1!filter2}
    @{ variable_name !! filter1!filter2 }

The filters are applied from left to right, so the above syntax is equvivalent to
the following call::

    @filter1(filter2(variable_name))

Example::

    @user.age!s
    @{user.age!!s}
    @{ user.age !!s }

Assuming the age property of user is integer we apply a string filter.

You are able to use custom filters, here is an example on how to use html escape
filter::

    try:
        from wheezy.html.utils import escape_html as escape
    except ImportError:
        import cgi
        escape = cgi.escape

    # ... initialize Engine.
    engine.global_vars.update({'e': escape})

First we try import an optimized version of html escape from `wheezy.html`_
package and if it is not available fallback to the one from the ``cgi`` package. Next we
update the engine's global variables with the escape function, which is accessible as the ``e``
filter name in template::

    @user.name!e
    @{ user.name !! e }

You are able use engine ``global_vars`` dictionary in order to simplify your
template access to some commonly used variables.


R-value expressions
~~~~~~~~~~~~~~~~~~~

You can use single line r-value expresions that evaluates to a rendered
value::

    @{ accepted and 'YES' or 'NO' }
    @{ (age > 20 and age < 120) and 'OK' or '?' }
    @{ n > 0 and 1 or -1 !! s }


Line Statements
~~~~~~~~~~~~~~~

The following python line statements are supported: `if`, `else`, `elif`,
`for`. Here is simple example::

    @require(items)
    @if items:
        @for i in items:
            @i.name: $i.price!s.
        @end
    @else:
        No items found.
    @end

Comments
~~~~~~~~

Only single line comments are supported::

    @# TODO:

Line Join
~~~~~~~~~

In case you need continue a long line without breaking it with new line during
rendering use line join (``\``)::

    @if menu_name == active:
        <li class='active'> \
    @else:
        <li> \
    @endif

Inheritance
~~~~~~~~~~~

Template inheritance allows you to build a master template that contains common
layout of your site and defines areas that a child templates can override.


Master Template
^^^^^^^^^^^^^^^

Master template is used to provide common layout of your site. Let's define
a master template (name ``shared/master.html``)::

    <html>
        <head>
            <title>
            @def title():
            @end
            @title() - My Site</title>
        </head>
        <body>
            <div id="content">
                @def content():
                @end
                @content()
            </div>
            <div id="footer">
                @def footer():
                &copy; Copyright 2012 by Me.
                @end
                footer()
            </div>
        </body>
    </html>

In this example, the @def tags define python functions (substitution areas).
These functions are inserted into a specific places (right after definition).
These places become place holders for child templates. The @footer place holder
defines default content while @title and @content are just empty.

Child Template
^^^^^^^^^^^^^^

Child templates are used to extend master templates via the defined place holders::

    @extends("shared/master.html")

    @def title():
        Welcome
    @end

    @def content():
        <h1>Home</h1>
        <p>
            Welcome to My Site!
        </p>
    @end

In this example, the @title and @content place holders are overriden by the child
template.

Note, *@import* and *@require* tokens are allowed at *@extends* token
level.

Include
~~~~~~~

The include is useful to insert a template content just in place of the statement::

    @include("shared/snippet/script.html")

Import
~~~~~~

The import is used to reuse some code stored in other files. So you are able
import all functions defined by that template::

    @import "shared/forms.html" as forms

    @forms.textbox('username')

or just certain name::

    @from "shared/forms.html" import textbox

    @textbox(name='username')

Once imported you use these names as variables in a template.

Code Extension
--------------

The :py:class:`~wheezy.template.ext.code.CodeExtension` includes support for
embedded python code. Syntax::

    @(
        # any python code
    )


Preprocessor
------------

The :py:class:`~wheezy.template.preprocessor.Preprocessor` processes templates
with syntax for the preprocessor engine and varying runtime templates (with runtime
engine factory) by some key function that is context driven. Here is an
example::

    from wheezy.html.utils import html_escape
    from wheezy.template.engine import Engine
    from wheezy.template.ext.core import CoreExtension
    from wheezy.template.ext.determined import DeterminedExtension
    from wheezy.template.loader import FileLoader
    from wheezy.template.preprocessor import Preprocessor

    def runtime_engine_factory(loader):
        engine = Engine(
            loader=loader,
            extensions=[
                CoreExtension(),
            ])
        engine.global_vars.update({
            'h': html_escape,
        })
        return engine

    searchpath = ['content/templates']
    engine = Engine(
        loader=FileLoader(searchpath),
        extensions=[
            CoreExtension('#', line_join=None),
            DeterminedExtension(['path_for', '_']),
        ])
    engine.global_vars.update({
    })
    engine = Preprocessor(runtime_engine_factory, engine,
                          key_factory=lambda ctx: ctx['locale'])

In this example, the :py:class:`~wheezy.template.preprocessor.Preprocessor` is
defined to use engine with the start token
defined as '#'. Any directives starting with ``#`` are processed once only
by the preprocessor engine. The ``key_factory`` is dependent on runtime context
and particularly on 'locale'. This way runtime engine factory is varied by
locale so locale dependent functions (``_`` and ``path_for``) are processed only
once by the preprocessor. See complete example in `wheezy.web`_ `demo.template`_
applicaiton.


.. _`wheezy.html`: http://pypi.python.org/pypi/wheezy.html
.. _`wheezy.web`: http://pypi.python.org/pypi/wheezy.web
.. _`demo.template`: https://bitbucket.org/akorn/wheezy.web/src/tip/demos/template/
