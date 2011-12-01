import logging
import sys

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from optparse import make_option

from django.core.management.base import NoArgsCommand

from setman.models import Settings
from setman.utils import AVAILABLE_SETTINGS, is_settings_container


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
        def store_values(settings, available_settings=None, prefix=None):
            available_settings = available_settings or AVAILABLE_SETTINGS

            for setting in available_settings:
                if is_settings_container(setting):
                    store_values(settings, setting, setting.app_name)
                elif not prefix:
                    setattr(settings, setting.name, setting.default)
                else:
                    data = settings.data

                    if not prefix in data:
                        data[prefix] = {}

                    data[prefix][setting.name] = setting.default

        try:
            settings = Settings.objects.get()
        except Settings.DoesNotExist:
            settings = Settings()
            if verbosity:
                print >> self.stdout, 'Will create new Settings instance.'
        else:
            if verbosity:
                print >> self.stdout, 'Settings instance already exist.'

        store_values(settings)
        settings.save()

        if verbosity:
            print >> self.stdout, 'Default values stored well!'
