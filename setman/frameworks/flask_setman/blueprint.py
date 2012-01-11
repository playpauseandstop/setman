from random import randint

from flask import Blueprint, Response, flash, redirect, render_template, \
    request, url_for

from setman import settings
from setman.frameworks.flask_setman.forms import settings_form_factory
from setman.frameworks.flask_setman.utils import update_form_fields
from setman.utils.auth import auth_permitted


setman_blueprint = Blueprint('setman', __name__, template_folder='templates')


@setman_blueprint.route('/edit', methods=('GET', 'POST'))
def edit():
    """
    Edit all available settings.
    """
    if not auth_permitted(request):
        output = render_template('setman/edit.html', auth_forbidden=True)
        return Response(output, status=403)

    settings_form = settings_form_factory()

    if request.method == 'POST':
        form = settings_form(request.form)

        if form.validate():
            form.save()

            flash('Settings have been succesfully updated.', 'success')
            return redirect('%s?%d' % (url_for('setman.edit'),
                                       randint(1000, 9999)))
    else:
        form = settings_form()

    return render_template('setman/edit.html', form=update_form_fields(form))


@setman_blueprint.route('/revert')
def revert():
    """
    Revert all settings to default values.
    """
    from setman import settings

    if not auth_permitted(request):
        output = render_template('setman/edit.html', auth_forbidden=True)
        return Response(output, status=403)

    settings.revert()
    flash('Settings have been reverted to default values.', 'success')

    return redirect('%s?%d' % (url_for('setman.edit'), randint(1000, 9999)))
