from django.core.exceptions import ValidationError


def abc_validator(value):
    return word_validator(value, 'abc')


def test_runner_validator(value):
    if not value.endswith('Runner'):
        raise ValidationError('%r value is not valid test runner.' % value)


def word_validator(value, word):
    words = value.split(' ')
    if not word in words:
        raise ValidationError('Value does not contain %s word.' % word)


def xyz_validator(value):
    return word_validator(value, 'xyz')
