.PHONY: test test-integration publish

DIST_DIR := dist
REPOSITORY ?= testpypi
PYTHON ?= .venv/bin/python

ifeq ($(REPOSITORY),testpypi)
PUBLISH_URL := https://test.pypi.org/legacy/
else ifeq ($(REPOSITORY),pypi)
PUBLISH_URL := https://upload.pypi.org/legacy/
else
$(error Unsupported REPOSITORY '$(REPOSITORY)'; use REPOSITORY=testpypi or REPOSITORY=pypi)
endif

test:
	$(PYTHON) -m pytest -m "not integration" -v

test-integration:
	$(PYTHON) -m pytest -m integration -v

publish:
	rm -rf $(DIST_DIR)
	uv build --out-dir $(DIST_DIR)
	uvx twine check $(DIST_DIR)/*
	uvx twine upload --repository-url $(PUBLISH_URL) $(DIST_DIR)/*
