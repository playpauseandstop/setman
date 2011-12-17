def task_bootstrap():
    """
    Continue booststraping with virtualenv and dependecies installed.
    """
    return {'actions': ['cp -n local_settings.py.def local_settings.py'],
            'file_dep': ['local_settings.py.def'],
            'targets': ['local_settings.py']}


def task_test():
    """
    Run application-related tests with required settings.
    """
    return {'actions': ['ve/bin/python manage.py test core setman']}
