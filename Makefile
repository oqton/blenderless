.EXPORT_ALL_VARIABLES:

# CONFIGURATION
VENV_NAME=.venv
# make poetry create local venv
POETRY_VIRTUALENVS_IN_PROJECT=true

.PHONY: test
test: $(VENV_NAME)
	poetry run pytest tests/ -vv --cov=blenderless --cov-report=html --cov-report term:skip-covered

$(VENV_NAME): | poetry.lock
	poetry install -vvv
	poetry show --tree
	poetry run bpy_post_install
	poetry run pre-commit install

poetry.lock:
	poetry lock -vvv

clean:
	rm -r .venv
	rm poetry.lock

pre-commit: $(VENV_NAME)
	poetry run pre-commit

pre-commit-all: $(VENV_NAME)
	poetry run pre-commit run --all-files
