#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='django-fileflatpages',
    version='0.1',
    author='Keegan Carruthers-Smith',
    author_email='keegan.csmith@gmail.com',
    url='https://bitbucket.org/keegan_csmith/django-fileflatpages',
    description='Django App for storing FlatPage fixtures per file.',
    packages=find_packages(exclude=('example_project*',)),
    install_requires=['Django'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development'
    ],
)
