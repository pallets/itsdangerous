.PHONY: clean-pyc test tox-test upload-docs

all: clean-pyc test

test:
	python tests.py

tox-test:
	tox

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

upload-docs:
	$(MAKE) -C docs html
	python setup.py upload_docs
