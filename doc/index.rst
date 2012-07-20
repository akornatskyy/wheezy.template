.. _`wheezy.template`:

Wheezy Template
===============

Introduction
------------

:ref:`wheezy.template` is a `python`_ package written in pure Python code.
It is a lightweight template library. The design goals achived:

* **Compact, Expressive, Clean:** Minimizes the number of keystrokes required
  to build a template. Enables fast and well read coding. You do not need to
  explicitly denote statement blocks within HTML (unlike other template
  systems), the parser is smart enough to understand your code. This enables
  a compact and expressive syntax which is really clean and just pleasure
  to type.
* **Intuitive, No time to Learn:** Basic Python programming skills
  plus HTML markup. You are productive just from start. Use full power
  of Python with minimal markup required to denote python statements.
* **Do Not Repeat Yourself:** Master layout templates for inheritance;
  include and import directives for maximum reuse.
* **Blazingly Fast:** The most effective python code offers the maximum
  rendering performance; ultimate speed and context preprocessor features.

Simple template::

    @require(user, items)
    Welcome, @user.name!
    @if items:
        @for i in items:
            @i.name: $i.price!s.
        @end
    @else:
        No items found.
    @end

It is optimized for performance, well tested and documented.

Resources:

* `source code`_, `examples`_ and `issues`_ tracker are available
  on `bitbucket`_
* `documentation`_, `readthedocs`_
* `eggs`_ on `pypi`_

Contents
--------

.. toctree::
   :maxdepth: 2

   gettingstarted
   examples
   userguide
   modules

.. _`bitbucket`: http://bitbucket.org/akorn/wheezy.template
.. _`documentation`: http://packages.python.org/wheezy.template
.. _`eggs`: http://pypi.python.org/pypi/wheezy.template
.. _`examples`: http://bitbucket.org/akorn/wheezy.template/src/tip/demos
.. _`issues`: http://bitbucket.org/akorn/wheezy.template/issues
.. _`pypi`: http://pypi.python.org
.. _`python`: http://www.python.org
.. _`readthedocs`: http://readthedocs.org/builds/wheezytemplate/
.. _`source code`: http://bitbucket.org/akorn/wheezy.template/src
