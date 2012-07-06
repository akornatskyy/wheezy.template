
"""
"""

from wheezy.template.comp import allocate_lock
from wheezy.template.loader import DictLoader


class Preprocessor(object):

    def __init__(self, runtime_engine_factory, engine, key_factory):
        self.lock = allocate_lock()
        self.runtime_engines = {}
        self.runtime_engine_factory = runtime_engine_factory
        self.engine = engine
        self.key_factory = key_factory
        template_class = self.engine.template_class
        self.engine.template_class = lambda name, render_template: \
            template_class(name, self.render)

    def get_template(self, name):
        return self.engine.get_template(name)

    def render(self, name, ctx, local_defs, super_defs):
        try:
            runtime_engine = self.runtime_engines[
                self.key_factory(ctx)]
        except KeyError:
            runtime_engine = self.ensure_runtime_engine(
                self.key_factory(ctx))
        try:
            return runtime_engine.renders[name](ctx, local_defs, super_defs)
        except KeyError:
            self.preprocess_template(runtime_engine, name, ctx)
            return runtime_engine.renders[name](ctx, local_defs, super_defs)

    # region: internal details

    def ensure_runtime_engine(self, key):
        self.lock.acquire(1)
        try:
            engines = self.runtime_engines
            if key in engines:
                return engines[key]
            engine = engines[key] = self.runtime_engine_factory(
                loader=DictLoader({}))

            def render(name, ctx, local_defs, super_defs):
                try:
                    return engine.renders[name](ctx, local_defs, super_defs)
                except KeyError:
                    self.preprocess_template(engine, name, ctx)
                    return engine.renders[name](ctx, local_defs, super_defs)
            engine.global_vars['_r'] = render
            return engine
        finally:
            self.lock.release()

    def preprocess_template(self, runtime_engine, name, ctx):
        self.lock.acquire(1)
        try:
            if name not in runtime_engine.renders:
                source = self.engine.render(name, ctx, {}, {})
                runtime_engine.loader.templates[name] = source
                runtime_engine.compile_template(name)
                del runtime_engine.loader.templates[name]
        finally:
            self.lock.release()
