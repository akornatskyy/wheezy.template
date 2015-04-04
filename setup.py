#!/usr/bin/env python

import os

try:
    from setuptools import setup
except:
    from distutils.core import setup  # noqa

extra = {}
try:
    from Cython.Build import cythonize
    p = os.path.join('src', 'wheezy', 'template')
    extra['ext_modules'] = cythonize(
        [os.path.join(p, '*.py'),
         os.path.join(p, 'ext', '*.py')],
        exclude=[os.path.join(p, '__init__.py'),
                 os.path.join(p, 'ext', '__init__.py')],
        nthreads=2, quiet=True)
except ImportError:
    pass

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='wheezy.template',
    version='0.1',
    description='A lightweight template library',
    long_description=README,
    url='https://bitbucket.org/akorn/wheezy.template',

    author='Andriy Kornatskyy',
    author_email='andriy.kornatskyy at live.com',

    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Widget Sets',
        'Topic :: Text Processing :: Markup :: HTML'
    ],
    keywords='html markup template preprocessor',
    packages=['wheezy', 'wheezy.template', 'wheezy.template.ext'],
    package_dir={'': 'src'},
    namespace_packages=['wheezy'],

    zip_safe=False,
    install_requires=[
    ],
    extras_require={
        'dev': [
            'coverage',
            'nose',
            'pytest',
            'pytest-pep8',
            'pytest-cov',
        ]
    },
    entry_points={
        'console_scripts': [
            'wheezy.template=wheezy.template.console:main'
        ]
    },

    platforms='any',
    **extra
)
