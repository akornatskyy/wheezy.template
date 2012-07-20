
Examples
========

Before we proceed let setup `virtualenv`_ environment::

    $ virtualenv env
    $ env/bin/easy_install wheezy.template

Big Table
---------

The big table demo compares `wheezy.template` with other template
engines in terms of how fast a table with 10 columns x 1000 rows can be
generated::

    @require(table)
    <table>
        @for row in table:
        <tr>
            @for key, value in row.items():
            <td>@key!h</td><td>@value!s</td>
            @end
        </tr>
        @end
    </table>

Install packages used in benchmark test::

    env/bin/easy_install -O2 jinja2 mako tenjin \
      tornado wheezy.html wheezy.template

Download `bigtable.py`_ source code and run it::

    $ env/bin/python bigtable.py
    jinja2                         40.22ms  24.86rps
    list_append                    19.85ms  50.39rps
    list_extend                    18.71ms  53.46rps
    mako                           36.19ms  27.63rps
    tenjin                         28.97ms  34.52rps
    tornado                        55.91ms  17.89rps
    wheezy_template                19.99ms  50.02rps

.. image:: static/bench1.png

Real World
----------

There is real world example available in `wheezy.web`_ package. It can be found
in `demo.template`_ application.

.. _`virtualenv`: http://pypi.python.org/pypi/virtualenv
.. _`bigtable.py`: https://bitbucket.org/akorn/wheezy.template/src/tip/demos/bigtable/bigtable.py
.. _`wheezy.web`: http://pypi.python.org/pypi/wheezy.web
.. _`demo.template`: https://bitbucket.org/akorn/wheezy.web/src/tip/demos/template
