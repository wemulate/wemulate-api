.PHONY: clean virtualenv test docker dist dist-upload

clean:
	find . -name '*.py[co]' -delete

virtualenv:
	poetry install
	@echo
	@echo "VirtualENV Setup Complete. Now run: poetry shell"
	@echo

test:
	python -m pytest \
		-v \
		--cov=wemulate-api \
		--cov-report=term \
		--cov-report=html:coverage-report \
		tests/

dist: clean
	rm -rf dist/*
	poetry build

dist-upload:
	twine upload dist/*