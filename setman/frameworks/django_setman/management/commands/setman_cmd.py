import logging
import sys

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from optparse import make_option

from django.core.management.base import NoArgsCommand

from setman import settings
from setman.frameworks.django_setman.models import Settings
from setman.utils.parsing import is_settings_container


AVAILABLE_SETTINGS = settings.available_settings
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
            print >> self.stdout, 'Project settings:'
            print >> self.stdout, 'Configuration definition file placed at ' \
                                  '%r\n' % AVAILABLE_SETTINGS.path

            for setting in AVAILABLE_SETTINGS:
                indent = ' ' * 4

                if is_settings_container(setting):
                    print >> self.stdout, '%s%r settings:' % \
                                          (indent, setting.app_name)
                    print >> self.stdout, '%sConfiguration definition file ' \
                                          'placed at %r' % \
                                          (indent, setting.path)
                    indent *= 2

                    for subsetting in setting:
                        print >> self.stdout, '%s%r' % (indent, subsetting)

                    print >> self.stdout
                else:
                    print >> self.stdout, '%s%r' % (indent, setting)

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
            Settings.objects.get()
        except Settings.DoesNotExist:
            if verbosity:
                print >> self.stdout, 'Will create new Settings instance.'
        else:
            if verbosity:
                print >> self.stdout, 'Settings instance already exist.'

        settings.revert()

        if verbosity:
            print >> self.stdout, 'Default values stored well!'
