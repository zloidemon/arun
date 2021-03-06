flake:
	pep8 arun/*.py examples/*.py
	pyflakes arun examples tests

test: flake
	py.test -s -q ./tests/

vtest: flake
	py.test -s ./tests/

build:
	python setup.py sdist bdist_wheel

cov cover coverage: flake
	py.test -s -v ./tests/ --cov=arun --cov=tests --cov-report=term
	@echo "open file://`pwd`/coverage/index.html"

clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -f `find . -type f -name '@*' `
	rm -f `find . -type f -name '#*#' `
	rm -f `find . -type f -name '*.orig' `
	rm -f `find . -type f -name '*.rej' `
	rm -f .coverage
	rm -rf build
	rm -rf cover
	rm -fr dist
	rm -fr *.egg-info
	python setup.py clean

.PHONY: all build venv flake test vtest testloop cov clean
