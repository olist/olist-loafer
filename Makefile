.PHONY: clean-pyc

default: test

clean-pyc:
	@find . -iname '*.py[co]' -delete
	@find . -iname '__pycache__' -delete
	@find . -iname '.coverage' -delete
	@rm -rf htmlcov/

clean-dist:
	@rm -rf dist/
	@rm -rf build/
	@rm -rf *.egg-info

clean: clean-pyc clean-dist

test:
	py.test -vv tests

test-cov:
	py.test -vv --cov=loafer tests

cov:
	coverage report -m

cov-report:
	py.test -vv --cov=loafer --cov-report=html tests

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel

release: dist
	git tag `python setup.py -q version`
	git push origin `python setup.py -q version`
	twine upload dist/*