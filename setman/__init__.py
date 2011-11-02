try:
    from setman.lazy import LazySettings
except ImportError:
    # Do not care about "Settings cannot be imported, because environment
    # variable DJANGO_SETTINGS_MODULE is undefined." errors
    LazySettings = type('LazySettings', (object, ), {})


__all__ = ('get_version', 'settings')


VERSION = (0, 1, 'beta')
settings = LazySettings()


def get_version(version=None):
    """
    Return setman version number in human readable form.

    You could call this function without args and in this case value from
    ``setman.VERSION`` would be used.
    """
    version = version or VERSION
    if len(version) > 2 and version[2] is not None:
        if isinstance(version[2], int):
            return '%d.%d.%d' % version
        return '%d.%d-%s' % version
    return '%d.%d' % version[:2]
