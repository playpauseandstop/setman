import logging

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from ConfigParser import Error as ConfigParserError, SafeConfigParser
from decimal import Decimal
from json import JSONEncoder

from setman.utils import importlib


__all__ = ('DEFAULT_SETTINGS_FILENAME', 'ConfigParser', 'ConfigParserError',
           'SetmanJSONEncoder', 'force_bool', 'load_from_path', 'logger')


DEFAULT_SETTINGS_FILENAME = 'settings.cfg'
logger = logging.getLogger('setman')


class ConfigParser(SafeConfigParser, object):
    """
    Customize default behavior for config parser instances to support config
    files without sections at all.
    """
    no_sections_mode = False
    optionxform = lambda _, value: value

    def _read(self, fp, fpname):
        """
        If "No Sections Mode" enabled - add global section as first line of
        file handler.
        """
        if self.no_sections_mode:
            global_section = StringIO()
            global_section.write('[DEFAULT]\n')
            global_section.write(fp.read())
            global_section.seek(0)
            fp = global_section

        return super(ConfigParser, self)._read(fp, fpname)


class SetmanJSONEncoder(JSONEncoder):
    """
    Add support of ``Decimal`` instances to ``JSONEncoder`` used on dumping
    and loading json.
    """
    def default(self, value):
        if isinstance(value, Decimal):
            return str(value)
        return super(SetmanJSONEncoder, self).default(value)


def force_bool(value):
    """
    Convert string value to boolean instance.
    """
    if isinstance(value, (bool, int)):
        return bool(value)

    boolean_states = ConfigParser._boolean_states
    if not value.lower() in boolean_states:
        return None

    return boolean_states[value.lower()]


def load_from_path(path):
    """
    Load class or function from string path.
    """
    module, attr = path.rsplit('.', 1)
    mod = importlib.import_module(module)
    return getattr(mod, attr)
