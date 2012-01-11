from setman import settings
from setman.backends.django import Backend as DjangoBackend
from setman.backends.django.models import Settings


__all__ = ('model_from_backend', )


def model_from_backend():
    """
    Return ``Settings`` model if currently used backend is Django.
    """
    if not settings._configured:
        settings.autoconf()

    if isinstance(settings._backend, DjangoBackend):
        return Settings

    return None
