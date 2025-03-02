## Pre-commit hooks

We use (pre-commit hooks)[https://pre-commit.com/] for several actions mostly using ruff:
- Linting including sorting of imports
- Formatting according to Pep 8

``
pre-commit install
pre-commit run --all-files
``

## Testing and coverage

``
coverage run -m pytest
coverage report
``

