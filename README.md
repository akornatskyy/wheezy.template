# wheezy.template

[![tests](https://github.com/akornatskyy/wheezy.template/actions/workflows/tests.yml/badge.svg)](https://github.com/akornatskyy/wheezy.template/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/akornatskyy/wheezy.template/badge.svg?branch=master)](https://coveralls.io/github/akornatskyy/wheezy.template?branch=master)
[![Documentation Status](https://readthedocs.org/projects/wheezytemplate/badge/?version=latest)](https://wheezytemplate.readthedocs.io/en/latest/?badge=latest)
[![pypi version](https://badge.fury.io/py/wheezy.template.svg)](https://badge.fury.io/py/wheezy.template)

[wheezy.template](https://pypi.org/project/wheezy.template/) is a
[python](https://www.python.org) package written in pure Python code. It
is a lightweight template library. The design goals achived:

- **Compact, Expressive, Clean:** Minimizes the number of keystrokes
  required to build a template. Enables fast and well read coding. You
  do not need to explicitly denote statement blocks within HTML
  (unlike other template systems), the parser is smart enough to
  understand your code. This enables a compact and expressive syntax
  which is really clean and just pleasure to type.
- **Intuitive, No time to Learn:** Basic Python programming skills
  plus HTML markup. You are productive just from start. Use full power
  of Python with minimal markup required to denote python statements.
- **Do Not Repeat Yourself:** Master layout templates for inheritance;
  include and import directives for maximum reuse.
- **Blazingly Fast:** Maximum rendering performance: ultimate speed
  and context preprocessor features.

Simple template:

```txt
@require(user, items)
Welcome, @user.name!
@if items:
    @for i in items:
        @i.name: @i.price!s.
    @end
@else:
    No items found.
@end
```

It is optimized for performance, well tested and documented.

Resources:

- [source code](https://github.com/akornatskyy/wheezy.template),
  [examples](https://github.com/akornatskyy/wheezy.template/tree/master/demos)
  and [issues](https://github.com/akornatskyy/wheezy.template/issues)
  tracker are available on
  [github](https://github.com/akornatskyy/wheezy.template)
- [documentation](https://wheezytemplate.readthedocs.io/en/latest/)

## Install

[wheezy.template](https://pypi.org/project/wheezy.template/) requires
[python](https://www.python.org) version 3.8+. It is independent of
operating system. You can install it from
[pypi](https://pypi.org/project/wheezy.template/) site:

```sh
pip install -U wheezy.template
```

If you run into any issue or have comments, go ahead and add on
[github](https://github.com/akornatskyy/wheezy.template).
