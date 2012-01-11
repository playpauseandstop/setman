class SetmanError(Exception):
    """
    Base class for each exception raised by ``setman`` library.
    """


class DoesNotExist(SetmanError):
    """
    """


class ImproperlyConfigured(SetmanError):
    """
    """


class SettingDoesNotExist(DoesNotExist):
    """
    """


class SettingTypeDoesNotExist(DoesNotExist):
    """
    """


class ValidationError(SetmanError):
    """
    """
