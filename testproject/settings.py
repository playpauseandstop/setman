import os


DIRNAME = os.path.normpath(os.path.dirname(__file__))

# ===============
# Django settings
# ===============
#
# --------------
# Admin settings
# --------------
ADMINS = ()
MANAGERS = ADMINS

# -------------------
# Admin CRUD settings
# -------------------
ADMIN_MEDIA_PREFIX = '/admin-media/'

# -----------------------
# Authentication settings
# -----------------------
AUTHENTICATION_BACKENDS = ('django_odesk.auth.backends.TeamAuthBackend', )

# --------------
# Cache settings
# --------------
CACHE_BACKEND = 'locmem://'

# -----------------
# Database settings
# -----------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DIRNAME, 'sqlite3.db'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# ----------------------
# Date and time settings
# ----------------------
TIME_ZONE = 'UTC'

# --------------
# Debug settings
# --------------
DEBUG = False
TEMPLATE_DEBUG = DEBUG

# -----------------------
# Installed apps settings
# -----------------------
#
# Init Test Project apps for use by Django-Jenkins to calculate coverage and
# run pylint only over this apps
#
PROJECT_APPS = ('setman', 'testproject.core')
BASE_INSTALLED_APPS = (
    # Django apps
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',

    # 3rd party apps
    'django_extensions',
    'django_jenkins',
    'south',
) + PROJECT_APPS
LOCAL_INSTALLED_APPS = ()

# ----------------------------
# Language and locale settings
# ----------------------------
USE_I18N = True
USE_L10N = True
LANGUAGE_CODE = 'en-us'

# ----------------
# Logging settings
# ----------------
BASE_LOGGING = {
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'DEBUG',
        },
        'null': {
            'class': 'django.utils.log.NullHandler',
            'level': 'DEBUG',
        }
    },
    'loggers': {},
    'version': 1,
}
LOCAL_LOGGING = {}

# --------------------
# Media files settings
# --------------------
MEDIA_ROOT = os.path.join(DIRNAME, 'media')
MEDIA_URL = '/media/'
SERVE_STATIC_FILES = False

# -------------------
# Middleware settings
# -------------------
BASE_MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)
LOCAL_MIDDLEWARE_CLASSES = ()

# ----------------
# Session settings
# ----------------
SESSION_COOKIE_NAME = 'testproject_sid'

# -----------------
# Template settings
# -----------------
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
)
TEMPLATE_DIRS = (
    os.path.join(DIRNAME, 'templates'),
)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# -------------------------------
# Other necessary Django settings
# -------------------------------
ROOT_URLCONF = 'testproject.urls'
SECRET_KEY = 'please, set up proper value in local_settings.py module'


# ==============
# oDesk settings
# ==============
#
# --------------------------------------------------
# oDesk users that will have access to admin section
# --------------------------------------------------
ODESK_ADMINS = (
    'denplis@odesk.com',
    'patrick-smith@odesk.com',
    'playpauseandstop@odesk.com',
    'yyurevich@odesk.com',
)
ODESK_SUPERUSERS = ODESK_ADMINS

# -------------------------------------------------------------
# Only users from next oDesk teams will have access to the site
# -------------------------------------------------------------
ODESK_AUTH_TEAMS = (
    'odesk:odeskps',
    'odesk:odeskpsbootcamp',
    'odesk:odeskpsinternal',
    'odeskfraudpreven:mqodeskpsdev',
    'odesk:odeskrnd',
    'google:tools',
    'google:toolsbootcamp',
)

# Empty tuples to prevent ``AttributeError`` on backend's ``authenticate``
# method
ODESK_AUTH_ADMIN_TEAMS = ()
ODESK_AUTH_SUPERUSER_TEAMS = ()
ODESK_AUTH_USERS = ()

# ====================
# setman configuration
# ====================
SETMAN_ADDITIONAL_TYPES = (
    'testproject.core.utils.IPAddressSetting',
)
# Allow edit settings to any user
SETMAN_AUTH_PERMITTED = lambda user: True

# ===================
# South configuration
# ===================
SOUTH_TESTS_MIGRATE = False


try:
    from local_settings import *
except ImportError:
    pass


INSTALLED_APPS = BASE_INSTALLED_APPS + LOCAL_INSTALLED_APPS
LOGGING = BASE_LOGGING.copy()
LOGGING.update(LOCAL_LOGGING)
MIDDLEWARE_CLASSES = BASE_MIDDLEWARE_CLASSES + LOCAL_MIDDLEWARE_CLASSES
