from django.conf import settings as django_settings


__all__ = ('auth_permitted', )


def auth_permitted(user):
    """
    Check that the user can have access to the view.
    """
    default = lambda user: user.is_superuser
    func = getattr(django_settings, 'SETMAN_AUTH_PERMITTED', default)
    return func(user)
