"""
"""

import sys

try:
    from wheezy.html.utils import escape_html as escape
except ImportError:
    try:
        from html import escape
    except ImportError:
        from cgi import escape

PY3 = sys.version_info[0] >= 3
s = PY3 and str or unicode  # noqa

ctx = {
    "table": [
        {
            "<a>": 1,
            "b": "<2>",
            "<c>": 3,
            "d": "<4>",
            "<e>": 5,
            "f": "<6>",
            "<g>": 7,
            "h": "<8>",
            "<i>": 9,
            "j": "<10>",
        }
        for x in range(1000)
    ]
}

tests = []


def test(n=100, name=None):
    if name:
        tests.append((name, None, None))
        return

    def decorator(f):
        tests.append((f.__name__[5:], f, n))

    return decorator


# region: python list append

if PY3:

    @test()
    def test_list_append():
        b = []
        w = b.append
        table = ctx["table"]
        w("<table>\n")
        for row in table:
            w("    <tr>\n")
            for key, value in row.items():
                w("        <td>")
                w(escape(key))
                w("</td><td>")
                w(str(value))
                w("</td>\n")
            w("    </tr>\n")
        w("</table>")
        return "".join(b)


else:

    @test()
    def test_list_append():  # noqa
        b = []
        w = b.append
        table = ctx["table"]
        w(u"<table>\n")
        for row in table:
            w(u"    <tr>\n")
            for key, value in row.items():
                w(u"        <td>")
                w(escape(key))
                w(u"</td><td>")
                w(s(value))
                w(u"</td>\n")
            w(u"    </tr>\n")
        w(u"</table>")
        return "".join(b)


# region: python join yield

if PY3:  # noqa: C901

    @test()
    def test_join_yield():
        def root():
            table = ctx["table"]
            yield "<table>\n"
            for row in table:
                yield "    <tr>\n"
                for key, value in row.items():
                    yield "        <td>"
                    yield escape(key)
                    yield "</td><td>"
                    yield s(value)
                    yield "</td>\n"
                yield "    </tr>\n"
            yield "</table>"

        return "".join(root())


else:

    @test()
    def test_join_yield():
        def root():
            table = ctx["table"]
            yield u"<table>\n"
            for row in table:
                yield u"    <tr>\n"
                for key, value in row.items():
                    yield u"        <td>"
                    yield escape(key)
                    yield u"</td><td>"
                    yield s(value)
                    yield u"</td>\n"
                yield u"    </tr>\n"
            yield u"</table>"

        return "".join(root())


# region: python list extend

if PY3:

    @test()
    def test_list_extend():
        b = []
        e = b.extend
        table = ctx["table"]
        e(("<table>\n",))
        for row in table:
            e(("    <tr>\n",))
            for key, value in row.items():
                e(
                    (
                        "        <td>",
                        escape(key),
                        "</td><td>",
                        s(value),
                        "</td>\n",
                    )
                )
            e(("    </tr>\n",))
        e(("</table>",))
        return "".join(b)


else:

    @test()
    def test_list_extend():  # noqa
        b = []
        e = b.extend
        table = ctx["table"]
        e((u"<table>\n",))
        for row in table:
            e((u"    <tr>\n",))
            for key, value in row.items():
                e(
                    (
                        u"        <td>",
                        escape(key),
                        u"</td><td>",
                        s(value),
                        u"</td>\n",
                    )
                )
            e((u"    </tr>\n",))
        e((u"</table>",))
        return "".join(b)


# region: wheezy.template

try:
    from wheezy.template.engine import Engine
    from wheezy.template.ext.core import CoreExtension
    from wheezy.template.loader import DictLoader
except ImportError:
    test(name="wheezy_template")
else:
    engine = Engine(
        loader=DictLoader(
            {
                "x": s(
                    """\
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
"""
                )
            }
        ),
        extensions=[CoreExtension()],
    )
    engine.global_vars.update({"h": escape})
    wheezy_template = engine.get_template("x")

    @test()
    def test_wheezy_template():
        return wheezy_template.render(ctx)


# region: Jinja2

try:
    from jinja2 import Environment
except ImportError:
    test(name="jinja2")
else:
    jinja2_template = Environment().from_string(
        s(
            """\
<table>
    {% for row in table: %}
    <tr>
        {% for key, value in row.items(): %}
        <td>{{ key | e }}</td><td>{{ value }}</td>
        {% endfor %}
    </tr>
    {% endfor %}
</table>
"""
        )
    )

    @test(30)
    def test_jinja2():
        return jinja2_template.render(ctx)


# region: tornado

try:
    from tornado.template import Template
except ImportError:
    test(name="tornado")
else:
    tornado_template = Template(
        s(
            """\
<table>
    {% for row in table %}
    <tr>
        {% for key, value in row.items() %}
        <td>{{ key }}</td><td>{{ value }}</td>
        {% end %}
    </tr>
    {% end %}
</table>
"""
        )
    )

    @test(10)
    def test_tornado():
        return tornado_template.generate(**ctx).decode("utf8")


# region: mako

try:
    from mako.template import Template
except ImportError:
    test(name="mako")
else:
    mako_template = Template(
        s(
            """\
<table>
    % for row in table:
    <tr>
        % for key, value in row.items():
        <td>${ key | h }</td><td>${ value }</td>
        % endfor
    </tr>
    % endfor
</table>
"""
        )
    )

    @test(30)
    def test_mako():
        return mako_template.render(**ctx)


# region: tenjin

try:
    import tenjin
except ImportError:
    test(name="tenjin")
else:
    try:
        import webext

        helpers = {"to_str": webext.to_str, "escape": webext.escape_html}
    except ImportError:
        helpers = {
            "to_str": tenjin.helpers.to_str,
            "escape": tenjin.helpers.escape,
        }
    tenjin_template = tenjin.Template(encoding="utf8")
    tenjin_template.convert(
        s(
            """\
<table>
    <?py for row in table: ?>
    <tr>
        <?py for key, value in row.items(): ?>
        <td>${ key }</td><td>#{ value }</td>
        <?py #end ?>
    </tr>
    <?py #end ?>
</table>
"""
        )
    )

    @test(40)
    def test_tenjin():
        return tenjin_template.render(ctx, helpers)


# region: web2py

try:
    import cStringIO
    from gluon.html import xmlescape
    from gluon.template import get_parsed
except ImportError:
    test(name="web2py")
else:
    # see gluon.globals.Response
    class DummyResponse(object):
        def __init__(self):
            self.body = cStringIO.StringIO()

        def write(self, data, escape=True):
            if not escape:
                self.body.write(str(data))
            else:
                self.body.write(xmlescape(data))

    web2py_template = compile(
        get_parsed(
            s(
                """\
<table>
    {{ for row in table: }}
    <tr>
        {{ for key, value in row.items(): }}
        <td>{{ =key }}</td><td>{{ =value }}</td>
        {{ pass }}
    </tr>
    {{ pass }}
</table>
"""
            )
        ),
        "",
        "exec",
    )

    @test(1)
    def test_web2py():
        response = DummyResponse()
        exec(web2py_template, {}, dict(response=response, **ctx))
        return response.body.getvalue().decode("utf8")


# region: djang

try:
    import django
    from django.conf import settings

    settings.configure(
        TEMPLATES=[
            {"BACKEND": "django.template.backends.django.DjangoTemplates"}
        ]
    )
    django.setup()
    from django.template import Context, Template
except ImportError:
    test(name="django")
else:
    django_template = Template(
        s(
            """\
<table>
    {% for row in table %}
    <tr>
        {% for key, value in row.items %}
        <td>{{ key }}</td><td>{{ value }}</td>
        {% endfor %}
    </tr>
    {% endfor %}
</table>
"""
        )
    )

    @test(1)
    def test_django():
        return django_template.render(Context(ctx))


# region: chameleon

try:
    from chameleon.zpt.template import PageTemplate
except ImportError:
    test(name="chameleon")
else:
    chameleon_template = PageTemplate(
        s(
            """\
<table>
    <tr tal:repeat="row table">
        <i tal:omit-tag="" tal:repeat="key row">
        <td>${key}</td><td>${row[key]}</td>
        </i>
    </tr>
</table>
"""
        )
    )

    @test(10)
    def test_chameleon():
        return chameleon_template.render(**ctx)


# region: cheetah

try:
    from Cheetah.Template import Template
except ImportError:
    test(name="cheetah3")
else:
    cheetah_ctx = {}
    cheetah_template = Template(
        s(
            """\
<table>
    #for $row in $table
    <tr>
        #for $key, $value in $row.items
        #filter WebSafe
        <td>$key</td>
        #end filter
        #filter None
        <td>$value</td>
        #end filter
        #end for
    </tr>
    #end for
</table>
"""
        ),
        searchList=[cheetah_ctx],
    )

    @test(5)
    def test_cheetah3():
        cheetah_ctx.update(ctx)
        output = cheetah_template.respond()
        cheetah_ctx.clear()
        return output


# region: spitfire

try:
    import spitfire
    import spitfire.compiler.util
except ImportError:
    test(name="spitfire")
else:
    spitfire_template = spitfire.compiler.util.load_template(
        s(
            """\
#from cgi import escape
<table>
    #for $row in $table
    <tr>
        #for $key, $value in $row.items()
        <td>${key|filter=escape}</td><td>$value</td>
        #end for
    </tr>
    #end for
</table>
"""
        ),
        "spitfire_template",
        spitfire.compiler.analyzer.o3_options,
        {"enable_filters": True},
    )

    @test(1)
    def test_spitfire():
        return spitfire_template(search_list=[ctx]).main()


# region: qpy

try:  # noqa: C901
    from qpy import join_xml, xml, xml_quote
except ImportError:
    test(name="qpy_list_append")
else:
    if PY3:

        @test(1)
        def test_qpy_list_append():
            b = []
            w = b.append
            table = ctx["table"]
            w(xml("<table>\n"))
            for row in table:
                w(xml("<tr>\n"))
                for key, value in row.items():
                    w(xml("<td>"))
                    w(xml_quote(key))
                    w(xml("</td><td>"))
                    w(value)
                    w(xml("</td>\n"))
                w(xml("</tr>\n"))
            w(xml("</table>"))
            return join_xml(b)

    else:

        @test(1)
        def test_qpy_list_append():
            b = []
            w = b.append
            table = ctx["table"]
            w(xml(u"<table>\n"))
            for row in table:
                w(xml(u"<tr>\n"))
                for key, value in row.items():
                    w(xml(u"<td>"))
                    w(xml_quote(key))
                    w(xml(u"</td><td>"))
                    w(value)
                    w(xml(u"</td>\n"))
                w(xml(u"</tr>\n"))
            w(xml(u"</table>"))
            return join_xml(b)


# region: bottle

try:
    from bottle import SimpleTemplate
except ImportError:
    test(name="bottle")
else:
    bottle_template = SimpleTemplate(
        s(
            """\
<table>
    % for row in table:
    <tr>
        % for key, value in row.items():
        <td>{{key}}</td><td>{{!value}}</td>
        % end
    </tr>
    % end
</table>
"""
        )
    )

    @test(30)
    def test_bottle():
        return bottle_template.render(**ctx)


# region: chevron

try:
    import chevron
except ImportError:
    test(name="chevron")
else:
    chevron_template = tuple(
        chevron.tokenizer.tokenize(
            """
<table>
    {{#table}}
    <tr>
        {{#.}}
        <td>{{key}}</td><td>{{value}}</td>
        {{/.}}
    </tr>
    {{/table}}
</table>
"""
        )
    )
    ctx2 = {
        "table": [
            {"key": k, "value": v}
            for row in ctx["table"]
            for k, v in row.items()
        ]
    }

    @test(1)
    def test_chevron():
        return chevron.render(chevron_template, ctx2)


# region: liquid

try:
    from liquid import Liquid
except ImportError:
    test(name="liquid")
else:
    liquid_args = [
        s(
            """
<table>
    {% for row in table %}
    <tr>
        {% for key in row %}
        <td>{{key | escape}}</td><td>{{row[key] | str | escape}}</td>
        {% endfor %}
    </tr>
    {% endfor %}
</table>
"""
        )
    ]
    if PY3:
        liquid_args.append({"mode": "python"})
    liquid_template = Liquid(*liquid_args)

    @test(1)
    def test_liquid():
        return liquid_template.render(**ctx)


# region: pybars3

try:
    from pybars import Compiler
except ImportError:
    test(name="pybars3")
else:
    compiler = Compiler()
    pybars3_template = compiler.compile(
        s(
            """
<table>
    {{#each table }}
    <tr>
        {{#each . }}
        <td>{{@key}}</td><td>{{.}}</td>
        {{/each}}
    </tr>
    {{/each}}
</table>
"""
        )
    )

    @test(1)
    def test_pybars3():
        return pybars3_template(ctx)


def run():
    import profile
    from pstats import Stats
    from timeit import repeat

    print("                     msec    rps  tcalls  funcs")
    for name, test, number in sorted(tests):
        if test:
            try:
                st = Stats(
                    profile.Profile().runctx("test()", globals(), locals())
                )
                t = min(repeat(test, number=number))
                print(
                    "%-17s %7.2f %6.2f %7d %6d"
                    % (
                        name,
                        1000 * t / number,
                        number / t,
                        st.total_calls,
                        len(st.stats),
                    )
                )
            except Exception:
                print("%-26s failed" % name)
        else:
            print("%-26s not installed" % name)


if __name__ == "__main__":
    run()
