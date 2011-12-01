=============================
Configuration Definition File
=============================

Format
======

Configuration Definition File should use any format that could be parsed by
Python standard :py:class:`ConfigParser.ConfigParser` instance.

And the next requirement is to using uppercased setting names, not camelcased
or lowercased. All letters in section name (that responds to setting name)
**should** be uppercased.

For example, test project used next configuration definition file::

    [BOOLEAN_SETTING]
    type = boolean
    default = false
    label = Boolean
    help_text = Simple checkbox field for boolean setting.

    [CHOICE_SETTING]
    type = choice
    choices = apple, grape, peach, pear, waterlemon
    default = pear
    label = Choice
    help_text = Select one of the available fruits.

    [DECIMAL_SETTING]
    type = decimal
    default = 8.5
    max_digits = 4
    decimal_places = 2
    min_value = 0
    max_value = 10
    label = Decimal
    help_text = Enter threshold after which bonus would be paid. Between 0 and 10.

    [INT_SETTING]
    type = int
    min_value = 16
    max_value = 32
    default = 24
    label = Int
    help_text = Enter your best age between 16 and 32 :)

    [FLOAT_SETTING]
    type = float
    default = 80.4
    label = Float
    help_text = Enter any float value. No validators would be used.
    wrong_arg = This argument won't be available after parsing.

    [STRING_SETTING]
    type = string
    default = Started with s
    regex = ^(s|S)
    label = String
    help_text = Please start your text with s letter.

    [VALIDATOR_SETTING]
    type = string
    required = false
    label = Validator
    help_text = Make sure that setting value will contain abc and xyz words.
    validators = testproject.core.validators.abc_validator,
                 testproject.core.validators.xyz_validator

Supported setting types
=======================

``django-setman`` supports not all possible setting types, but we think, most
common used.

Each setting type supports next arguments:

* **type**

  Only **REQUIRED** argument for each setting block. Right now next types
  are supported: boolean, choice, decimal, float, int, string.

* **required**

  Will setting require value or could be blank?

* **default**

  Default setting value. It's very useful to have default value setup if you
  want later using the "Revert" mode.

* **label**

  How setting would be labeled in UI. By default, would be used setting name.

* **help_text**

  Short description about setting.

* **validators**

  Comma-separated string which later would be parsed to validators list. See
  `Validators`_ section for more info.

Boolean
-------

Simple boolean setting.

In UI would be converted to ``django.forms.BooleanField`` not-required field.

Choice
------

String choice setting. Need to have additional argument:

* **choices**

  A comma-seprated list of available choices to use. In very common case, you
  may just be enough with it. But you also may provide choices in more advanced
  way.

  For example, if you need labels use next format::

      choices = (key, Value), (another_key, Another Value)

  And if you need groups::

      choices = Group { (key, Value) }, Another Group { (another_key, Another Value) }

  And finally, you can just provide Python path where list or tuple with
  choices located, like::

      choices = testproject.core.choices.ROLE_CHOICES
      choices = testproject.core.models.UserProfile.ROLE_CHOICES
      choices = core.UserProfile.ROLE_CHOICES

  .. note:: Don't worry these choices would be loaded only when setting needs
     to be converted to form field (in UI or before validation), so you don't
     need to care about import ordering.

In UI would be converted to ``django.forms.ChoiceField`` required field.

Decimal
-------

Decimal setting. Can have additional arguments:

* **max_digits**

  The maximum number of digits (those before the decimal point plus those
  after the decimal point, with leading zeros stripped) permitted in the
  value.

* **decimal_places**

  The maximum number of decimal places permitted.

* **max_value**
* **min_value**

  These control the range of values permitted in the field. They would be
  converted to decimal.

In UI would be converted to ``django.forms.DecimalField`` required field.

Float
-----

Float setting. Can have additional arguments:

* **max_value**
* **min_value**

  These control the range of values permitted in the field. They would be
  converted to float.

In UI would be converted to ``django.forms.FloatField`` required field.

Int
---

Integer setting. Can have additional arguments:

* **max_value**
* **min_value**

  These control the range of values permitted in the field. They would be
  converted to integer.

In UI would be converted to ``django.forms.IntegerField`` required field.

String
------

String setting. Can have additional arguments:

* **regex**

  A regular expression specified either as a string.

* **max_length**
* **min_length**

  If provided, these arguments ensure that the string is at most or at least
  the given length.

In UI would be converted to ``django.forms.CharField`` required field if not
**regex** argument provided or to ``django.forms.RegexField`` if does.

Validators
==========

The one of main goals of ``django-setman`` is providing ability to validate
setting values. In most cases you can deal with validation by setting specific
arguments, like ``regex``, ``max_length`` or ``min_length`` for the `String`_
settings.

But, when you need more complex validation rules you should use ``validators``
argument. Value there should be a comma separated list of Python pathes to
validator functions.

For example,

::

    [TEST_RUNNER]
    type = string
    default = django.test.simple.DjangoTestRunner
    validators = testproject.core.validators.test_runner_validator

So, on parsing ``django-setman`` tries to load ``test_runner_validator`` from
``testproject.core.validators`` module and if not fail silently (but leaves
a message to logs).

.. note:: Don't worry these validators would be loaded only when setting needs
   to be converted to form field (in UI or before validation), so you don't
   need to care about import ordering.

The ``test_runner_validator`` should be an easy function, that raises
``django.core.exceptions.ValidationError`` if value isn't proper, e.g.::

    from django.core.exceptions import ValidationError


    def test_suite_runner(value):
        if not value.endswith('TestRunner'):
            raise ValidationError('Specify valid test runner.')

And after if you try to setup not proper value in code or in UI the setman
will raise an error or show you error message in UI.

::

    In [1]: from setman import settings

    In [2]: settings.TEST_RUNNER = 'testproject.core.NotTestRunnerClass'

    In [3]: settings.save()
    ...
    ValidationError: {'data': [u'Specify valid test runner.']}

Different default values for different environments
===================================================

Sometimes, we need to provide different default values for different
environments. Saying, at production we need to use values from config
definition file, when at staging we need to use different values.

And rewriting all config definition file for staging isn't an answer, why we
need two files, that not relate each other and indeed sometime later we'll
miss to change necessary thing at one of these files.

So, the answer is provide simple config file in next format::

    SETTING_NAME = <default>

and then setup ``SETMAN_DEFAULT_VALUES_FILE`` with path to it. Now,
``django-setman`` would be use default values from this source instead of
config definition file.

Configuration definiton file for the app
========================================

.. note:: New in 0.3 release.

The main idea of giving ability to use app configuration definition files
alongside with global (project) configuration definition files is support of
configuring reusable apps with ``setman``.

So, if we have ``giggling`` app and want to customize its settings via
``setman`` UI and then read these settings with ``setman.settings`` instance
we need to do next steps:

1. Provide ``settings.cfg`` file in ``giggling`` app directory.
2. Add ``giggling`` app to the ``INSTALLED_APPS`` list (and add empty
   ``models.py`` module if app hasn't it yet, cause we load all apps via
   ``django.db.models.loading.get_apps`` method and anyway you'll need
   ``models.py`` module even empty to test your app ;) )
3. Enable ``setman``. That's all.

Now, if configuration definition file for ``giggling`` app is::

    [GIGGLE_IN]
    type = int
    default = 60
    label = Giggle in
    help_text = Giggle one time per x seconds.
    min_value = 0

    [GIGGLE_PROVIDER]
    type = string
    default = giggling.GiggleProvider
    label = Giggle provider
    help_text = Which class would be used for giggling. Should be an ancestor
                of giggling.BaseGiggleProvider class.
    validators = giggling.validators.validate_giggle_provider

You should access to these settings as::

    from setman import settings

    from giggling import load_provider

    def giggle(request):
        giggle_in = settings.giggling.GIGGLE_IN
        giggle_provider = load_provider(settings.giggling.GIGGLE_PROVIDER)
        ...

And what if you need to customize some giggle things in some project, saying
change default value of ``GIGGLE_IN`` setting and setup more enhanced validator
to the ``GIGGLE_PROVIDER`` setting? It's easy, in project configuration
definition file you'll need to do something next::

    ...
    [giggling.GIGGLE_IN]
    default = 30

    [giggling.GIGGLE_PROVIDER]
    validators = project.core.validators.super_validate_giggle_provider

And now ``setman`` use values of these attributes for giggling settings.

.. important:: You can redefine each available setting attribute except
   ``type``. Setting type is stable value and can setup only one time in app
   configuration definition file.
