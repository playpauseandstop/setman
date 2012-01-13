================================
Test Projects for setman library
================================

``setman`` comes with simple test projects that made for check how library
works.

Django
======

Initialization
--------------

Bootstrap testproject with::

    $ cd testproject-django
    $ python bootstrap.py

Then init database and setman migrations::

    $ cd ..
    $ python testproject-django/manage.py syncdb --noinput
    $ python testproject-django/manage.py migrate --noinput

And finally you can to get pair of oDesk keys and setup it to
``local_settings.py`` module. After, feel free to run development server::

    $ make django_server

and check how ``setman`` Django test project works.

Run tests
---------

For running tests, check that project already bootstrapped. If all ok, just
run standard Django test command::

    $ make django_test

.. note:: We don't need to provide custom test settings module. All necessary
   options setup at ``testproject.settings`` and your ``local_settings``.

Also project has **Jenkins** support (via ``django-jenkins`` app). So to run
complete Jenkins tasks, execute::

    $ python testproject-django/manage.py jenkins

and then check for data in ``reports/`` directory.

Flask
=====

Initialization
--------------

Bootstrap testproject with::

    $ cd testproject-flask
    $ python bootstrap.py

And right after you're ready to run Flask server with::

    $ make flask_server

and check how ``setman`` Flask test project works.

Run tests
---------

For running tests, check that project already bootstrapped. If all ok, just
run test with::

    $ make flask_test

No framework
============

Initialization
--------------

You don't need to bootstrap testproject, cause it doesn't use any external
libraries.

Run app
-------

::

    $ make -C testproject-noframework app
    $ FORMAT=(ini|json|pickle) make -C testproject-noframework app

Test application just read settings from configurationd definition files and
provide ability to edit these settings.

Run tests
---------

For running tests, execute next command::

    $ make -C testproject-noframework test

Running all available tests
===========================

After you bootstrapped all test project, you could to run all available tests
with::

    $ make test
