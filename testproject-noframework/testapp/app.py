#!/usr/bin/env python
#
# Simple console app to test how ``setman`` library works with no frameworks
# and with json or ini filebased backend.
#
import logging
import os

from setman import settings
from setman.utils.parsing import is_settings_container


if 'LOGGING' in os.environ:
    logging.basicConfig(level=logging.INFO)

DEFAULT_FORMAT = 'json'
DIRNAME = os.path.dirname(__file__)
rel = lambda *parts: os.path.abspath(os.path.join(DIRNAME, *parts))

SETTINGS_DATA_FILE = rel('settings.%(format)s')
SETTINGS_FILE = rel('settings.cfg')
SETTINGS_FILES = {'testapp': rel('testapp.cfg')}


def configure_settings(format):
    settings.configure(
        backend='setman.backends.filebased',
        filename=SETTINGS_DATA_FILE % {'format': format},
        format=format,
        settings_file=SETTINGS_FILE,
        settings_files=SETTINGS_FILES
    )


def main(available_settings=None):
    available_settings = available_settings or settings.available_settings
    app_name = available_settings.app_name

    if not app_name:
        print('Found %d available setting(s)' % len(available_settings))

    for mixed in available_settings:
        if is_settings_container(mixed):
            main(mixed)
        else:
            setting = mixed
            values = getattr(settings, app_name) if app_name else settings
            old_value = getattr(values, setting.name)

            print('\n%s (%s)' % (setting.label, setting.help_text))
            new_value = raw_input('Enter new value, old value is %r: ' % \
                                  old_value)

            if not new_value:
                new_value = old_value

            setattr(values, setting.name, new_value)

    if not available_settings.app_name:
        settings.save()
        print('\nSettings were saved! Exit...')


if __name__ == '__main__':
    format = os.environ.get('FORMAT', DEFAULT_FORMAT)
    configure_settings(format)

    main()
