import typing

# See
# http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__("pkg_resources").declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path

    __path__: typing.List[str] = extend_path(  # type: ignore[no-redef]
        __path__, __name__
    )
