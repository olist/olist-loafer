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
	hatch run pytest -vv tests

test-cov:
	hatch run pytest -vv --cov=loafer tests

cov:
	hatch run coverage report -m

cov-report:
	hatch run pytest -vv --cov=loafer --cov-report=html tests

check-fixtures:
	hatch run pytest --dead-fixtures

dist: clean
	hatch build

release: dist
	git tag `hatch version`
	git push origin `hatch version`
	hatch publish

changelog-preview:
	@echo "\nmain ("$$(date '+%Y-%m-%d')")"
	@echo "-------------------\n"
	@git log $$(hatch version)...main --oneline --reverse
