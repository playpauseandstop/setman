from setman import settings
from setman.utils.parsing import is_settings_container


__all__ = ('get_config', )


def get_config(name, default=None):
    """
    Helper function to easy fetch ``name`` from database or django settings and
    return ``default`` value if setting key isn't found.

    But if not ``default`` value is provided (``None``) the ``AttributeError``
    exception can raised if setting key isn't found.

    If ``name`` is one of available ``app_name`` function raises
    ``ValueError`` cause cannot to returns config value.

    For fetching app setting use next definition:
    ``<app_name>.<setting_name>``.
    """
    app_name = None

    if '.' in name:
        app_name, name = name.split('.', 1)

    values = getattr(settings, app_name) if app_name else settings

    if default is not None:
        result = getattr(values, name) if hasattr(values, name) else default
    else:
        result = getattr(values, name)

    if is_settings_container(result):
        raise ValueError('%r is settings container, not setting.' % name)

    return result
