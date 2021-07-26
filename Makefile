
#!make
.PHONY: init lint format test publish clean
SHELL := /bin/bash

# Globals
PROJECT_NAME = httpx_iap
VENV_PATH = .venv
VENV_PYTHON = $(VENV_PATH)/bin/python3

all: init format format lint test build

init:
	poetry install
	poetry version

lint:
	poetry run flake8 --max-line-length=100 src/$(PROJECT_NAME)
	poetry run pylint src/$(PROJECT_NAME)
	poetry run mypy src/$(PROJECT_NAME)
	poetry run bandit -r src/$(PROJECT_NAME)

format:
	poetry run black src/$(PROJECT_NAME)
	poetry run black tests

test:
	poetry run pytest --junitxml=build/reports/all.xml -o junit_family=xunit2 --cov=httpx_iap --cov-fail-under=100 tests

build:
	poetry build

publish: env build
	poetry publish

clean:
	rm -rf $(VENV_PATH)
	rm -rf **/__pycache__
	rm -rf **/.ipynb_checkpoints
	rm -rf $(REPO).egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf build
	rm -rf dist