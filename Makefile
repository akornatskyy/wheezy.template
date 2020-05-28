.SILENT: clean env po nose-cover test-cover qa test doc release upload
.PHONY: clean env po nose-cover test-cover qa test doc release upload

all: clean nose-cover test qa release

debian:
	apt-get -y update ; \
	apt-get -y dist-upgrade ; \
	apt-get -y --no-install-recommends install libbz2-dev build-essential \
		python python-dev python-setuptools python-virtualenv

clean:
	find demos/ -type d -name __pycache__ | xargs rm -rf
	find demos/ -name '*.py[co]' -delete
	find src/ -type d -name __pycache__ | xargs rm -rf
	find src/ -name '*.py[co]' -delete
	rm -rf dist/ build/ doc/_build MANIFEST src/*.egg-info .cache .coverage

release:
	python setup.py -q sdist

upload:
	REV=$$(git rev-list --count HEAD) ; \
	sed -i "s/'0.1'/'0.1.$$REV'/" src/wheezy/template/__init__.py ; \
	twine upload dist/wheezy.template-0.1.$$REV.tar.gz

qa:
	flake8 --max-complexity 10 demos doc src setup.py \
	&& pycodestyle demos doc src setup.py

test:
	pytest -q -x --pep8 --doctest-modules src/wheezy/template

test-cover:
	pytest -q --cov-report term-missing \
		--cov wheezy.template src/wheezy/template

benchmark:
	pytest demos/bigtable/bigtable.py

doc:
	sphinx-build -a -b html doc/ doc/_build/

test-demos:
	@pytest -q -x --pep8 demos/**/*.py
