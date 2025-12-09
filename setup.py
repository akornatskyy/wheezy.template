#!/usr/bin/env python

import os
from glob import glob

from setuptools import Extension, setup  # type: ignore[import]


def module_name_from_src_path(path: str) -> str:
    """Derive a fully-qualified module name from a file path under ./src.

    Cython's default path-to-module logic relies on finding __init__.py files.
    For PEP 420 namespace packages (e.g. "wheezy"), that inference stops too
    early, which can produce incorrect module names (e.g. "template.*").
    """

    rel = os.path.relpath(path, "src")
    rel_no_ext = os.path.splitext(rel)[0]
    return rel_no_ext.replace(os.sep, ".")


def optional_cython_extensions() -> object:
    try:
        from Cython.Build import cythonize  # type: ignore[import]
    except ImportError:
        return None

    package_root = os.path.join("src", "wheezy", "template")

    sources: list[str] = []
    sources.extend(glob(os.path.join(package_root, "*.py")))
    sources.extend(glob(os.path.join(package_root, "ext", "*.py")))

    extensions: list[Extension] = []
    for src_path in sources:
        if os.path.basename(src_path) == "__init__.py":
            continue
        extensions.append(
            Extension(module_name_from_src_path(src_path), [src_path])
        )

    return cythonize(
        extensions,
        nthreads=2,
        compiler_directives={"language_level": 3},
        quiet=True,
    )


def main() -> None:
    extra = {}
    ext_modules = optional_cython_extensions()
    if ext_modules is not None:
        extra["ext_modules"] = ext_modules

    setup(**extra)


if __name__ == "__main__":
    main()
