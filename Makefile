# Setup Django project
django_project = testproject-django
django_python = $(django_project)/ve/bin/python
djake = VIRTUALENV=$(django_project)/ve djake
DJANGO_RUNSERVER ?= runserver
DJANGO_IP ?= 0.0.0.0
DJANGO_PORT ?= 4331
DJANGO_SHELL ?= shell_plus

# Django test settings
DJANGO_TEST_APPS ?= testapp
DJANGO_TEST_ARGS ?=

# Setup Flask project
flask_project = testproject-flask
flask_python = PYTHONPATH=.:$(flask_project) $(flask_project)/ve/bin/python
FLASK_IP ?= 0.0.0.0
FLASK_PORT ?= 4332
FLASK_SHELL ?= $(flask_project)/ve/bin/ipython
FLASK_TEST_ARGS ?=

clean:
	find . -name '*.pyc' -delete

distclean: clean
	-rm -rf build/
	-rm -rf dist/

django_bootstrap:
	cd $(django_project) && python bootstrap.py

django_server:
	$(djake) $(DJANGO_RUNSERVER) $(DJANGO_IP):$(DJANGO_PORT)

django_shell:
	$(djake) $(DJANGO_SHELL)

django_test:
	$(djake) test $(DJANGO_TEST_ARGS) $(DJANGO_TEST_APPS)

flask_bootstrap:
	cd $(flask_project) && python bootstrap.py

flask_shell:
	PYTHONPATH=.:$(flask_project) $(FLASK_SHELL)

flask_server:
	$(flask_python) $(flask_project)/run.py $(FLASK_IP):$(FLASK_PORT)

flask_test:
	$(flask_python) $(flask_project)/testapp/tests.py $(FLASK_TEST_ARGS)

test: clean django_test flask_test
	$(MAKE) -C testproject-noframework test
