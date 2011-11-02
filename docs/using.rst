===================
Using django-setman
===================

First of all, you'll need to install ``django-setman``. To do this, just
execute::

    $ pip install django-setman

After, add ``setman`` to your ``INSTALLED_APPS`` option,

::

    INSTALLED_APPS = (
        ...
        'setman',
        ...
    )

And finaly include ``setman.urls`` on your project's root URLConf module::

    urlpatterns = patterns('',
        ...
        (r'^setman/', include('setman.urls')),
        ...
    )

That's all!

On existed projects
===================

First of all, you need to run syncdb or migrate command (if your project
supports South),

::

    $ python manage.py syncdb --noinput
    $ python manage.py migrate --noinput

Next you may need to convert your custom project settings to the `Configuration
Definiton File <config>`_ format.

For example,

::

    WRITER_DEFAULT_RATE = 7.00
    WRITER_SCORE_CUTOFF = 5.33
    WRITER_BONUS_SCORE = 8.5
    WRITER_BONUS = 120

should be converted to::

    [WRITER_DEFAULT_RATE]
    type = decimal
    default = 7
    max_digits = 5
    decimal_places = 2
    min_value = 1

    [WRITER_SCORE_CUTOFF]
    type = decimal
    default = 5.33
    max_digits = 4
    decimal_places = 2
    min_value = 0
    max_value = 10

    [WRITER_BONUS_SCORE]
    type = decimal
    default = 8.5
    max_digits = 4
    decimal_places = 2
    min_value = 0
    max_value = 10

    [WRITER_BONUS]
    type = int
    default = 120
    min_value = 100

And finally you need to run custom management command that check how settings
parsed and if all ok store settings to database with default values.

::

    $ python manage.py setman_cmd -d

On new projects
===============

For new projects, you'll need do same things, init database table for
``django-setman`` app, provide configuration definition file and store default
settings to the database.

And also we recommend to start using `South <http://south.aeracode.org/>`_ app
from the beginning.
