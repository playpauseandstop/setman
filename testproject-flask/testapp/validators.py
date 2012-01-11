from wtforms.validators import ValidationError


def abc_validator(value):
    return word_validator(value, 'abc')


def word_validator(value, word):
    words = value.split(' ')
    if not word in words:
        raise ValidationError('Value does not contain %s word.' % word)


def xyz_validator(value):
    return word_validator(value, 'xyz')
