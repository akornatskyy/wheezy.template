#!/usr/bin/env python

import os
import re

from setuptools import setup  # type: ignore[import]


def run_build():
    extra = {}
    try:
        from Cython.Build import cythonize  # type: ignore[import]

        p = os.path.join("src", "wheezy", "template")
        extra["ext_modules"] = cythonize(
            [os.path.join(p, "*.py"), os.path.join(p, "ext", "*.py")],
            exclude=[
                os.path.join(p, "__init__.py"),
                os.path.join(p, "ext", "__init__.py"),
            ],
            compiler_directives={"language_level": 3},
            quiet=True,
        )
    except ImportError:
        pass

    readme = open("README.md").read()
    version = (
        re.search(  # type: ignore
            r'__version__ = "(.+)"',
            open("src/wheezy/template/__init__.py").read(),
        )
        .group(1)
        .strip()
    )

    setup(
        name="wheezy.template",
        version=version,
        python_requires=">=3.10",
        description="A lightweight template library",
        long_description=readme,
        long_description_content_type="text/markdown",
        url="https://github.com/akornatskyy/wheezy.template",
        author="Andriy Kornatskyy",
        author_email="andriy.kornatskyy@live.com",
        license="MIT",
        classifiers=[
            "Environment :: Web Environment",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3.13",
            "Programming Language :: Python :: 3.14",
            "Programming Language :: Python :: Implementation :: CPython",
            "Programming Language :: Python :: Implementation :: PyPy",
            "Topic :: Internet :: WWW/HTTP",
            "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Software Development :: Widget Sets",
            "Topic :: Text Processing :: Markup :: HTML",
        ],
        keywords="html markup template preprocessor",
        packages=["wheezy", "wheezy.template", "wheezy.template.ext"],
        package_data={"wheezy.template": ["py.typed"]},
        package_dir={"": "src"},
        namespace_packages=["wheezy"],
        zip_safe=False,
        install_requires=[],
        entry_points={
            "console_scripts": ["wheezy.template=wheezy.template.console:main"]
        },
        platforms="any",
        **extra
    )


if __name__ == "__main__":
    run_build()
