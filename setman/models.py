from django.core.cache import cache
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode

from setman.fields import SettingsField
from setman.managers import CACHE_KEY, SettingsManager


__all__ = ('Settings', )


class Settings(models.Model):
    """
    Store all custom project settings in ``data`` field as ``json`` dump.
    """
    data = SettingsField(_('data'), blank=True, default='', editable=False)

    objects = SettingsManager()

    class Meta:
        verbose_name = _('settings')
        verbose_name_plural = _('settings')

    def __delattr__(self, name):
        if name.isupper():
            if name in self.data:
                del self.data[name]
        else:
            super(Settings, self).__delattr__(name)

    def __getattr__(self, name):
        if name.isupper():
            return self.data.get(name)
        return super(Settings, self).__getattr__(name)

    def __setattr__(self, name, value):
        if name.isupper():
            if not self.data:
                self.data = {}
            self.data[name] = value
        else:
            return super(Settings, self).__setattr__(name, value)

    def __unicode__(self):
        return force_unicode(_('Project settings'))

    def save(self, *args, **kwargs):
        """
        Do not store settings instance to database if another settings instance
        already stored there.
        """
        lookup = {} if not self.pk else {'pk': self.pk}
        counter = self._default_manager.exclude(**lookup).count()

        if counter:
            raise ValueError('Cannot save another Settings instance. %d '
                             'Settings instances(s) already exist there.' % \
                             counter)

        super(Settings, self).save(*args, **kwargs)


@receiver(signals.post_save, sender=Settings)
def clear_settings_cache(instance, **kwargs):
    """
    Clear settings cache and.
    """
    from setman import settings
    settings._clear()

    if CACHE_KEY in cache:
        cache.delete(CACHE_KEY)
