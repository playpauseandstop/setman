project = testapp
python = PYTHONPATH=.:.. python

app:
	$(python) $(project)/app.py

clean:
	find $(project) -name '*.pyc' -delete

distclean: clean
	rm -f $(project)/settings.ini
	rm -f $(project)/settings.json

test:
	$(python) $(project)/tests.py
