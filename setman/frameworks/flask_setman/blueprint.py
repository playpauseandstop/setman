from random import randint

from flask import Blueprint, flash, redirect, render_template, request, url_for

from setman.frameworks.flask_setman.utils import update_form_fields


setman_blueprint = Blueprint('setman', __name__, template_folder='templates')


@setman_blueprint.route('/edit', methods=('GET', 'POST'))
def edit():
    """
    Edit all available settings.
    """
    from setman.frameworks.flask_setman.forms import SettingsForm

    if request.method == 'POST':
        form = SettingsForm(request.form)

        if form.validate():
            form.save()

            flash('Settings have been succesfully updated.', 'success')
            return redirect('%s?%d' % (url_for('setman.edit'),
                                       randint(1000, 9999)))
    else:
        form = SettingsForm()

    return render_template('setman/edit.html', form=update_form_fields(form))


@setman_blueprint.route('/revert')
def revert():
    """
    Revert all settings to default values.
    """
    from setman import settings

    settings.revert()
    flash('Settings have been reverted to default values.', 'success')

    return redirect('%s?%d' % (url_for('setman.edit'), randint(1000, 9999)))
