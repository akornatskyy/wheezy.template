import getopt
import json
import os
import sys
import typing

from wheezy.template.engine import Engine
from wheezy.template.ext.code import CodeExtension
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import FileLoader

try:
    from wheezy.html.utils import escape_html as escape
except ImportError:  # pragma: nocover
    from html import escape


class Options:
    def __init__(
        self,
        token_start: str = "@",
        line_join: str = "\\",
        searchpath: typing.Optional[typing.List[str]] = None,
        extensions: typing.Optional[typing.List[str]] = None,
    ) -> None:
        self.token_start = token_start
        self.line_join = line_join
        self.searchpath = searchpath or ["."]
        self.extensions = extensions or []
        self.template = ""
        self.context: typing.List[str] = []


def main(argv: typing.Optional[typing.List[str]] = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if not args:
        return 2
    ts = args.token_start
    extensions = [CoreExtension(ts, args.line_join), CodeExtension(ts)]
    extensions.extend(args.extensions)
    engine = Engine(FileLoader(args.searchpath), extensions)
    engine.global_vars.update({"h": escape})
    t = engine.get_template(args.template)
    sys.stdout.write(t.render(load_context(args.context)))
    return 0


def load_context(sources: typing.List[str]) -> typing.Mapping[str, typing.Any]:
    c: typing.Dict[str, typing.Any] = {}
    args: typing.List[typing.Any] = []
    for s in sources:
        if os.path.isfile(s):
            d = json.load(open(s))
        else:
            d = json.loads(s)
        args.append(d)
        if isinstance(d, dict):
            c.update(d)
    c["__args__"] = args
    return c


def parse_args(  # noqa: C901
    args: typing.List[str],
) -> typing.Optional[Options]:
    try:
        opts, value = getopt.getopt(args, "s:t:j:wh")
    except getopt.GetoptError:
        e = sys.exc_info()[1]
        usage()
        print("error: %s" % e)
        return None
    d = Options(token_start="@", searchpath=["."], extensions=[])
    for o, a in opts:
        if o == "-h":
            usage()
            return None
        elif o == "-t":
            d.token_start = a
        elif o == "-j":
            d.line_join = a
        elif o == "-s":
            d.searchpath = a.split(";")
        elif o == "-w":  # pragma: nocover
            from wheezy.html.ext.template import WhitespaceExtension

            d.extensions.append(WhitespaceExtension())
    if not value:
        usage()
        return None
    d.template = value[0]
    d.context = value[1:]
    return d


def usage() -> None:
    from os.path import basename

    print(
        """\

Renders a template with the provided context.

Usage: %s template [ context ... ]

Positional arguments:
  template    The template filename.
  context     A filename or JSON string representing the context.

Optional arguments:
  -s path     Search path for templates (default ".").
  -t token    Token start (default "@").
  -j token    Line join token (default "\\").
  -w          Enable whitespace cleanup.
  -h          Show this help message.

The contexts passed are available as the __args__ list variable."""
        % basename(sys.argv[0])
    )


if __name__ == "__main__":  # pragma: nocover
    sys.exit(main())
