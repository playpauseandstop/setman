from setman.backends import SetmanBackend


class Backend(SetmanBackend):
    """
    Add support of Django ORM to ``setman`` library.
    """
    def read(self):
        from setman.backends.django.models import Settings

        try:
            instance = Settings.objects.get()
        except Settings.DoesNotExist:
            instance = Settings(data={})

        setattr(self, '_instance_cache', instance)
        return instance.data

    def save(self):
        instance = getattr(self, '_instance_cache')
        instance.data = self.data
        instance.save()
