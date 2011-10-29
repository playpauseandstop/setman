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

  A comma-seprated list of available choices to use.

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
