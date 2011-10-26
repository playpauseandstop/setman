import copy

from django.core.cache import cache
from django.db.models import Manager


__all__ = ('SettingsManager', )


CACHE_KEY = 'setman__settings'


class SettingsManager(Manager):

    def get(self, *args, **kwargs):
        if not CACHE_KEY in cache:
            instance = super(SettingsManager, self).get(*args, **kwargs)

            data = copy.deepcopy(instance.data)
            data.update({'pk': instance.pk})

            cache.set(CACHE_KEY, data)
        else:
            data = copy.deepcopy(cache.get(CACHE_KEY))
            pk = data.pop('pk')

            instance = self.model(data=data)
            instance.pk = pk

        return instance
