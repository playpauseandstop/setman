import logging
import os
import traceback

from flask import Flask, render_template, request

from setman import settings
from setman.helpers import get_config
from setman.utils.ordereddict import OrderedDict
from setman.utils.parsing import is_settings_container


if 'LOGGING' in os.environ:
    logging.basicConfig(level=logging.INFO)

DIRNAME = os.path.abspath(os.path.dirname(__file__))
rel = lambda *parts: os.path.abspath(os.path.join(DIRNAME, *parts))

SETMAN_ADDITIONAL_TYPES = ('testapp.utils.IPAddressSetting', )
SETMAN_SETTINGS_FILES = {'namespace': rel('namespace.cfg')}

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 't:\xc6\x1d\xcd\x86\xb7_\x11\x1e\xfe\xc1AD\x9f>'
app.static_folder = rel('..', '..', 'testproject-django', 'media')

settings.configure(framework='setman.frameworks.flask_setman',
                   app=app,
                   backend='setman.backends.filebased',
                   filename=rel('..', 'settings.json'),
                   format='json')


@app.route('/docs')
@app.route('/docs/<path>')
def docs(path=None):
    """
    View instructions on how to build documentation.
    """
    dirname = rel('..', '..')
    docs_dirname = rel('..', '..', 'docs', '_build', 'html')

    if not os.path.isdir(docs_dirname):
        return render_template('docs.html', dirname=dirname)
    elif path is None:
        return redirect(url_for('docs', path='index.html'))

    handler = open(os.path.join(docs_dirname, path))
    content = handler.read()
    handler.close()

    return content


@app.route('/favicon.ico')
def favicon():
    """
    Show favicon from static files.
    """
    return app.send_static_file('favicon.ico')


@app.route('/')
def home():
    """
    Home page.
    """
    return render_template('home.html')


@app.route('/sandbox', methods=('GET', 'POST'))
def sandbox():
    """
    Simple sandbox for testing values in ``setman.settings``.
    """
    def get_setman_names(available_settings=None):
        available_settings = available_settings or settings.available_settings
        data = []

        for setting in available_settings:
            if is_settings_container(setting):
                data.extend(get_setman_names(setting))
            else:
                name = '.'.join((setting.app_name, setting.name)) \
                       if setting.app_name else setting.name
                data.append(name)

        return data

    context = {'flask_names': sorted(app.config.keys()),
               'setman_names': get_setman_names()}

    if request.method == 'POST':
        if 'name' in request.form:
            has_traceback = False
            name = request.form['name']

            try:
                value = get_config(name)
            except:
                has_traceback = True
                value = traceback.format_exc()

            context.update({'has_traceback': has_traceback,
                            'has_value': True,
                            'name': name,
                            'value': value})

    return render_template('sandbox.html', **context)


@app.route('/view-settings')
def view_settings():
    """
    View all available configuration definition files.
    """
    path = settings.available_settings.path

    handler = open(path, 'rb')
    project_settings_content = handler.read()
    handler.close()

    apps_settings_contents = OrderedDict()

    for setting in settings.available_settings:
        if is_settings_container(setting):
            handler = open(setting.path, 'rb')
            apps_settings_contents[setting.app_name] = handler.read()
            handler.close()

    filename = app.config.get('SETMAN_DEFAULT_VALUES_FILE', None)

    if filename:
        handler = open(filename, 'rb')
        default_values_content = handler.read()
        handler.close()
    else:
        default_values_content = None

    context = {'apps_settings_contents': apps_settings_contents,
               'default_values_content': default_values_content,
               'project_settings_content': project_settings_content}
    return render_template('view_settings.html', **context)
