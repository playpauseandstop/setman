from setman.backends import SetmanBackend
from setman.backends.django.managers import CACHE_KEY


class Backend(SetmanBackend):
    """
    Add support of Django ORM to ``setman`` library.
    """
    @property
    def instance(self):
        from setman.backends.django.models import Settings

        try:
            return Settings.objects.get()
        except Settings.DoesNotExist:
            return Settings.objects.create(data={})

    def read(self):
        return self.instance.data

    def save(self):
        instance = self.instance
        instance.data = self.data
        instance.save()
