from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _


__all__ = ('UserProfile', )


class UserProfile(models.Model):
    """
    Simple User profile model.
    """
    ROLE_CHOICES = (
        (_('Content Creation'), (
            ('project_manager', _('Project Manager')),
            ('writer', _('Writer')),
            ('editor', _('Editor')),
            ('senior_editor', _('Senior Editor')),
        )),
        (_('Content Distribution'), (
            ('dist_project_manager', _('Project Manager')),
            ('dist_content_publisher', _('Publisher')),
            ('dist_content_reviewer', _('Reviewer')),
        ))
    )

    user = models.OneToOneField('auth.User', related_name='profile',
        verbose_name=_('user'))

    role = models.CharField(_('role'), max_length=32, choices=ROLE_CHOICES,
        default='writer')

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')


@receiver(signals.post_save, sender=User)
def auto_create_user_profile(instance, **kwargs):
    """
    Auto-create user profile instance after user saved.
    """
    try:
        instance.profile
    except ObjectDoesNotExist:
        UserProfile.objects.create(user=instance)
