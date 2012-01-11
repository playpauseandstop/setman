import re


def error(message):
    from setman import settings

    error_klass = settings._framework.ValidationError
    return error_klass(message)


def decimal_places_validator(decimal_places):
    def validator(value):
        sign, digits, exponent = value.as_tuple()
        decimals = abs(exponent)

        if decimals > decimal_places:
            raise error('Ensure that there are no more than %s decimal ' \
                        'places.' % decimal_places)

        return value
    return validator


def max_digits_validator(max_digits):
    def validator(value):
        sign, digits, exponent = value.as_tuple()

        if len(digits) > max_digits:
            raise error('Ensure that there are no more than %s digits in ' \
                        'total.' % max_digits)

        return value
    return validator


def max_length_validator(max_length):
    def validator(value):
        if len(value) > max_length:
            raise error('Ensure that length of value is less than or equal ' \
                        'to %s.' % max_length)
        return value
    return validator


def max_value_validator(max_value):
    def validator(value):
        if value > max_value:
            raise error('Ensure this value is less than or equal to %s.' % \
                        max_value)
        return value
    return validator


def min_length_validator(min_length):
    def validator(value):
        if len(value) < min_length:
            raise error('Ensure that length of value is greater than or ' \
                        'equal to %s.' % min_length)
        return value
    return validator


def min_value_validator(min_value):
    def validator(value):
        if value < min_value:
            raise error('Ensure this value is greater than or equal to %s.' % \
                        min_value)
        return value
    return validator


def regex_validator(regex):
    def validator(value):
        compiled = re.compile(regex)

        if not compiled.match(value):
            raise error('Enter a valid value.')

        return value
    return validator
