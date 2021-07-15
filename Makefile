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
	pytest -vv tests

test-cov:
	pytest -vv --cov=loafer tests

cov:
	coverage report -m

cov-report:
	pytest -vv --cov=loafer --cov-report=html tests

check-fixtures:
	pytest --dead-fixtures

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel

twine:
	pip install twine

release: twine clean dist
	git tag `python setup.py -q version`
	git push origin `python setup.py -q version`
	twine upload dist/*.whl dist/*.tar.gz

changelog-preview:
	@echo "\nmain ("$$(date '+%Y-%m-%d')")"
	@echo "-------------------\n"
	@git log $$(python setup.py -q version)...main --oneline --reverse
