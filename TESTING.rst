==============================
Test Project for django-setman
==============================

``django-setman`` comes with simple test project that made for check how
library works.

Initialization
==============

Bootstrap testproject with::

    $ cd testproject
    $ python bootstrap.py

Then init database and setman migrations::

    $ python manage.py syncdb --noinput
    $ python manage.py migrate --noinput

And finally you can to get pair of oDesk keys and setup it to
``local_settings.py`` module. After, feel free to run development server::

    $ python manage.py runserver <port>

and check how ``django-setman`` works.

Run tests
=========

For running tests, check that project already bootstrapped. If all ok, just
run standard Django test command::

    $ python manage.py test core setman

.. note:: We don't need to provide custom test settings module. All necessary
   options setup at ``testproject.settings`` and your ``local_settings``.

Also project has **Jenkins** support (via ``django-jenkins`` app). So to run
complete Jenkins tasks, execute::

    $ python manage.py jenkins

and then check for data in ``reports/`` directory.
