from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='code_monkey',

    version='0.0.3',

    description='A Python refactoring/static analysis tool',

    # The project's main homepage.
    url='https://github.com/ForSpareParts/code_monkey',

    # Author details
    author='David Jackson',
    author_email='altmail@jackson-wallace.net',

    # Choose your license
    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Code Generators',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    keywords='development code_generation static_analysis',

    packages=['code_monkey'],


    install_requires=[
        'wsgiref==0.1.2',
        'astroid==1.1.1',
        'logilab-common==0.61.0'
    ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'test': [
            'coverage==3.7.1',
            'nose==1.3.3',
        ],
        'dev': [
            'Sphinx==1.3.1',
            'sphinx-rtd-theme==0.1.8'
        ]
    },

)
