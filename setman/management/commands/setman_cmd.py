import logging
import sys

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from optparse import make_option

from django.core.management.base import NoArgsCommand

from setman.models import Settings
from setman.utils import AVAILABLE_SETTINGS


DEFAULT_ACTION = 'check_setman'
logger = logging.getLogger('setman')


class Command(NoArgsCommand):
    """
    """
    help_text = 'Check setman configuration or create Settings instance with '\
                'default values.'
    option_list = NoArgsCommand.option_list + (
        make_option('-d', '--default-values', action='store_true',
            default=False, dest='default_values',
            help='Store default values to Settings model.'),
    )

    def check_setman(self, verbosity):
        """
        Check setman configuration.
        """
        if verbosity:
            print >> self.stdout, 'Configuration definition file placed at ' \
                                  '%r' % AVAILABLE_SETTINGS.path
            print >> self.stdout, 'Available settings are:\n'

            for setting in AVAILABLE_SETTINGS:
                print >> self.stdout, '    %r' % setting

            print >> self.stdout, ''

    def handle_noargs(self, **options):
        """
        Do all necessary things.
        """
        default_values = options.get('default_values', False)
        verbosity = int(options.get('verbosity', 1))

        self.check_setman(verbosity)

        if default_values:
            self.store_default_values(verbosity)

    def store_default_values(self, verbosity):
        """
        Store default values to Settings instance.
        """
        try:
            settings = Settings.objects.get()
        except Settings.DoesNotExist:
            settings = Settings()
            if verbosity:
                print >> self.stdout, 'Will create new Settings instance.'
        else:
            if verbosity:
                print >> self.stdout, 'Settings instance already exist.'

        for setting in AVAILABLE_SETTINGS:
            setattr(settings, setting.name, setting.default)

        settings.save()
        if verbosity:
            print >> self.stdout, 'Default values stored well!'
