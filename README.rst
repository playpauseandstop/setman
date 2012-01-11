======
setman
======

Settings manager for Python web-apps and projects. Another?

The Great Idea
==============

Some time ago we at oDesk PS developed `django-setman
<http://github.com/odeskps/django-setman>`_ app, which is the answer if you
need to specify custom settings in your Django project and add ability to setup
these settings from UI (like Django admin CRUD).

But later, we thought, what if modify this app and make it universal? We mean,
not to use only with Django, but for example with Flask as well.

So please welcome ``setman`` - universal Python app to work with settings
that could be customized via UI.

Requirements
============

* `Python <http://www.python.org/>`_ 2.6 or 2.7

Supported frontends (frameworks)
================================

* `Django <http://www.djangoproject.com/>`_ 1.3 or higher
* `Flask <http://flask.pocoo.org/>`_ 0.8 or higher

Supported backends (ORM)
========================

* Django ORM
* File-based backend (supported formats: ini, json or pickle)

Installation
============

*On most UNIX-like systems, you'll probably need to run these commands as root
or using sudo.*

To install use::

    $ pip install setman

Or::

    $ python setup.py install

Also, you can retrieve fresh version of ``setman`` from `GitHub
<https://github.com/playpauseandstop/setman>`_::

    $ git clone git://github.com/playpauseandstop/setman.git

and place ``setman`` directory somewhere to ``PYTHONPATH`` (or ``sys.path``).

License
=======

``setman`` is licensed under the `BSD License
<https://github.com/playpauseandstop/setman/blob/master/LICENSE>`_.

Usage. More information
=======================

See full documentation at ``docs/`` directory or browse online `here
<http://packages.python.org/setman/>`_.

Bugs, feature requests?
=======================

If you found some bug in ``setman`` library, please, add new issue to the
project's `GitHub issues <https://github.com/playpauseandstop/setman/issues>`_.
