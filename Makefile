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

/usr/local/bin/package_cloud:
	sudo gem install package_cloud

package_cloud: /usr/local/bin/package_cloud

release: package_cloud clean dist
	git tag `python setup.py -q version`
	git push origin `python setup.py -q version`
	package_cloud push olist/v2/python dist/*.whl
	package_cloud push olist/v2/python dist/*.tar.gz

changelog-preview:
	@echo "\nmaster ("$$(date '+%Y-%m-%d')")"
	@echo "-------------------\n"
	@git log $$(python setup.py -q version)...master --oneline --reverse
