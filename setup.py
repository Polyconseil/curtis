#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


def read(file_path):
    with open(file_path) as fp:
        return fp.read()


setup(
    name='curtis',
    version='0.1',
    description="A simple sentry cli",
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: System :: Logging',
        'Topic :: Terminals',
        'Topic :: Utilities',
    ],
    keywords=['sentry', 'cli'],
    author='Polyconseil',
    author_email='opensource+curtis@polyconseil.fr',
    url='https://github.com/Polyconseil/curtis/',
    license='BSD',
    packages=find_packages(where='src'),
    package_dir={'': str('src')},
    include_package_data=True,
    zip_safe=False,
    setup_requires=[
        'setuptools',
    ],
    install_requires=[
        'click',
        'requests',
        'termcolor',
    ],
    entry_points={
        'console_scripts': (
            'curtis = curtis.__main__:main',
        ),
    },
)
