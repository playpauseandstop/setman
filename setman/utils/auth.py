from setman import settings
from setman.utils import importlib


__all__ = ('auth_permitted', )


def auth_permitted(request):
    """
    Check that the user in request can have access to the view or not.

    By default, all users can edit or revert settings values.
    """
    default = lambda request: True
    func = settings._framework.auth_permitted_func or default

    if isinstance(func, basestring):
        module, attr = func.split('.')

        mod = importlib.import_module(module)
        func = getattr(mod, attr)

    return func(request)
