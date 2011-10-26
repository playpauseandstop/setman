from django.db import models
from django.utils.translation import ugettext_lazy as _


__all__ = ('Settings', )


class Settings(models.Model):
    """
    Store all custom project settings in ``data`` field as ``json`` dump.
    """
    data = models.TextField(_('data'), blank=True, default='', editable=False)

    class Meta:
        verbose_name = _('settings')
        verbose_name_plural = _('settings')
