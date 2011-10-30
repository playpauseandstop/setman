=======================
Customize django-setman
=======================

For basic usage, you don't need to change any of next values in your project
settings file. But if you needs some more custom things, you're welcome.

SETMAN_ADDITIONAL_TYPES
=======================

By default, as you probably know, ``django-setman`` supports just boolean,
decimal, float, int and string setting types. But if you missed some setting
type you can add its support for library.

For this, first of all you'll need to create child to ``setman.utils.Setting``
class and provide ``type`` attribute there.

::

    from django import forms

    from setman.utils import Setting


    class IPAddressSetting(Setting):

        type = 'ip'
        field_klass = forms.IPAddressField

And then you should add this class to the ``SETMAN_ADDITIONAL_TYPES`` list or
tuple,

::

    SETMAN_ADDITIONAL_TYPES = (
        'testproject.utils.IPAddressSetting',
    )

Next, on configuration definition file you should use ``ip`` as setting type::

    [DO_NOT_BLOCK]
    type = ip
    default = 127.0.0.1

SETMAN_AUTH_PERMITTED
=====================

By default, only superusers can have access to the "Edit Settings" page. But
you can setup access for any user with this setting.

``SETMAN_AUTH_PERMITTED`` should be a callable object, ready to get ``user``
argument. If this lambda or function returns not false value user would be
granted access to the "Edit Settings" page.

Couple of examples.

1. Enable access not only for superusers, but for staff users as well::

    SETMAN_AUTH_PERMITTED = lambda user: user.is_staff or user.is_superuser

2. Enable access only for project managers (with using ``profile`` relation)::

    SETMAN_AUTH_PERMITTED = lambda user: user.profile.role == 'project_manager'

3. Enable access to any logged in project user::

    SETMAN_AUTH_PERMITTED = lambda user: True

SETMAN_DEFAULT_VALUES_FILE
==========================

By default, all default values read directly from config definition file, but
if you need to provide different values for different environment setup
path to the file with new default values, like::

    SETMAN_DEFAULT_VALUES_FILE = os.path.join(DIRNAME, 'production.cfg')

SETMAN_SETTINGS_FILE
====================

By default, configuration definition file should be placed at same directory
where ``DJANGO_SETTINGS_MODULE`` located and named as ``settings.cfg``, but if
you don't want to store ``.cfg`` files alongside with Python modules, you
should setup path where settings file is placed.

For example, if settings located in root directory and named same as project
named::

    SETMAN_SETTINGS_FILE = os.path.join(DIRNAME, '..', '<project>.cfg')

where ``<project`` - your project name and ``DIRNAME`` - path to directory
with global project settings.
