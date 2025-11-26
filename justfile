# List all recipes
default:
    @just --list


# Run all autoformattings
[no-exit-message]
format:
    ruff format .
    just ruff-check --fix


# Check Python files to detect bad coding habits
[no-exit-message]
ruff-check *FLAGS:
    uv run ruff check . {{FLAGS}}


# Check the formatting of the Python files
[no-exit-message]
ruff-format-check:
    uv run ruff format --check .


# Check type annotations
[no-exit-message]
mypy:
    uv run mypy .


# Run vulture, dead code analysis
[no-exit-message]
vulture:
    uv run vulture


# Run all linters at once
[no-exit-message]
lint:
    just ruff-check
    just ruff-format-check
    just mypy
    just vulture


# Run the unit tests
[no-exit-message]
test *FLAGS:
    uv run pytest {{FLAGS}}


# Remove artifact files
[no-exit-message]
clean:
    -find . -name "*.pyc" -exec rm -rf {} +
    -find . -name __pycache__ -exec rm -rf {} +
    -find . -name .ruff_cache -exec rm -rf {} +
    -find . -name .pytest_cache -exec rm -rf {} +
    -find . -name .mypy_cache -exec rm -rf {} +
    -rm -rf ./*id2iri_mapping*.json
    -rm -rf ./*id2iri_[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]*.json
    -rm -f ./warnings.log


# create the project json
[no-exit-message]
daschland-excel2json:
    dsp-tools excel2json daschland_ontology daschland.json

# create the data xml
[no-exit-message]
daschland-xmllib:
    uv run python src/xmllib/main.py
