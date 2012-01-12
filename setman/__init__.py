from setman.lazy import LazySettings


__all__ = ('VERSION', 'get_version', 'settings')


VERSION = (0, 1, 'alpha')
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
