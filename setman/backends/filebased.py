import json
import os
import re

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from setman.backends import SetmanBackend
from setman.exceptions import ImproperlyConfigured, ValidationError
from setman.utils import ConfigParser, SetmanJSONEncoder, logger
from setman.utils.ordereddict import OrderedDict
from setman.utils.parsing import is_settings_container


FilnameError = ImproperlyConfigured('Please, supply ``filename`` instance ' \
                                    'attr first.')


class Backend(SetmanBackend):
    """
    Backend to read and write settings values to text file using one of
    supported formats: 'ini', 'json', 'pickle'.

    Default format is 'json'.

    You should setup ``filename`` attribute to the backend, otherwise
    ``ImproperlyConfigured`` error would be raised.
    """
    encoder_cls = SetmanJSONEncoder
    format = 'json'
    filename = None
    filemode_to_read = 'r'
    filemode_to_save = 'w+'

    def __init__(self, **kwargs):
        super(Backend, self).__init__(**kwargs)
        self.format = self.format.lower()

    def from_python(self, data):
        data = self._batch_method('to_python', data)

        if self.format == 'ini':
            output = StringIO()
            old_data = data

            data, defaults = {}, {}

            for key, value in old_data.items():
                if isinstance(value, dict):
                    data[key] = value
                else:
                    defaults[key] = value

            config = ConfigParser(defaults=defaults)

            for section, subdata in data.items():
                if not config.has_section(section):
                    config.add_section(section)

                for key, value in subdata.items():
                    config.set(section, key, str(value))

            config.write(output)

            output.seek(0)
            return output.read()
        elif self.format == 'json':
            kwargs = self._prepare_json_kwargs(dumps=True)
            return json.dumps(data, **kwargs)
        elif self.format == 'pickle':
            return pickle.dumps(data)

        raise ImproperlyConfigured('File format %r is not supported.' % \
                                   self.format)

    @property
    def ignore_cache(self):
        if hasattr(self, 'disable_ignore_cache'):
            return False

        try:
            mtime = os.path.getmtime(self.filename)
        except (IOError, OSError):
            mtime = None

        if not mtime:
            return False

        old_mtime = getattr(self, '_mtime_cache', None)
        setattr(self, '_mtime_cache', mtime)

        if old_mtime and mtime != old_mtime:
            return True

        return False

    def read(self):
        if not self.filename:
            raise FilenameError

        try:
            handler = open(self.filename, self.filemode_to_read)
        except (IOError, OSError), e:
            message = 'Cannot open %r file for read in %r mode' % \
                      (self.filename, self.filemode_to_read)
            logger.error(message)

            return {}

        content = handler.read()
        handler.close()

        return self.to_python(content)

    def save(self):
        if not self.filename:
            raise FilenameError

        try:
            handler = open(self.filename, self.filemode_to_save)
        except (IOError, OSError), e:
            message = 'Cannot open %r file for write in %r mode' % \
                      (self.filename, self.filemode_to_save)
            logger.error(message)

            raise e

        setattr(self, 'disable_ignore_cache', True)
        content = self.from_python(self.data)
        delattr(self, 'disable_ignore_cache')

        handler.write(content)
        handler.close()

        # After writing data to file, clear all previous data cache and clear
        # validation error if any
        self.clear()

    def to_python(self, content):
        data = None

        if self.format == 'ini':
            output = StringIO(content)

            config = ConfigParser()
            config.readfp(output)

            data = config._defaults.copy()

            for section in config.sections():
                if not section in data:
                    data[section] = {}

                for key, value in config.items(section):
                    data[section].update({key: value})
        elif self.format == 'json':
            if content:
                kwargs = self._prepare_json_kwargs(loads=True)
                data = json.loads(content, **kwargs)
            else:
                data = {}
        elif self.format == 'pickle':
            data = pickle.loads(content)

        if data is None:
            raise ImproperlyConfigured('File format %r is not supported.' % \
                                       self.format)

        return self._batch_method('to_python', data)

    def _prepare_json_kwargs(self, dumps=False, loads=False):
        assert dumps or loads, 'Please, supply ``dumps`` or ``loads`` ' \
                               'keyword argument first.'

        if dumps:
            args = ('skipkeys', 'ensure_ascii', 'check_circural', 'allow_nan',
                    'cls', 'indent', 'separators', 'encoding', 'default')
        else:
            args = ('encoding', 'cls', 'object_hook', 'parse_float',
                    'parse_int', 'parse_constant', 'object_paris_hook')

        kwargs = {}

        for arg in args:
            cls_arg = 'cls'

            if arg == 'cls':
                cls_arg = 'encoder_cls' if dumps else 'decoder_cls'

            if not hasattr(self, arg) and not hasattr(self, cls_arg):
                continue

            value = getattr(self, cls_arg) if hasattr(self, cls_arg) \
                                           else getattr(self, arg)
            kwargs.update({arg: value})

        return kwargs
