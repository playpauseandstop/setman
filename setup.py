#!/usr/bin/env python

import os

from distutils.core import setup


DIRNAME = os.path.dirname(__file__)

readme = open(os.path.join(DIRNAME, 'README.rst'), 'r')
README = readme.read()
readme.close()

version = __import__('setman').get_version()


setup(
    name='setman',
    version=version,
    description='Settings manager for Python web-apps and projects. Another?',
    long_description=README,
    author='Igor Davydenko',
    author_email='playpauseandstop@gmail.com',
    maintainer='Igor Davydenko',
    maintainer_email='playpauseandstop@gmail.com',
    url='https://github.com/playpauseandstop/setman',
    packages=[
        'setman',
        'setman.backends',
        'setman.backends.django',
        'setman.frameworks',
        'setman.frameworks.django_setman',
        'setman.frameworks.django_setman.management',
        'setman.frameworks.django_setman.migrations',
        'setman.frameworks.flask_setman',
        'setman.utils',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Topic :: Utilities',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
    ],
    keywords='django flask settings manager',
    license='BSD License',
)
