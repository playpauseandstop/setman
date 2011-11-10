from setman import settings


__all__ = ('get_config', )


def get_config(name, default=None):
    """
    Helper function to easy fetch ``name`` from database or django settings and
    return ``default`` if setting key isn't found.

    But if not ``default`` value is provided (``None``) the ``AttributeError``
    exception can raised if setting key isn't found.
    """
    if default is not None:
        return getattr(settings, name, default)
    return getattr(settings, name)
