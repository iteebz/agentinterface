default:
    @just --list

clean:
    @echo "Cleaning agentinterface..."
    @rm -rf dist build .pytest_cache .ruff_cache __pycache__ node_modules
    @find . -type d -name "__pycache__" -exec rm -rf {} +
    @cd react && rm -rf dist build node_modules
    @cd python && rm -rf dist build .pytest_cache .ruff_cache .venv

install:
    @cd react && npm install
    @cd python && poetry lock
    @cd python && poetry install

ci:
    @node react/scripts/discover.mjs --quiet
    @cd react && npm run --silent lint:fix
    @cd react && npm run --silent format
    @cd python && poetry run ruff format . --quiet
    @cd python && poetry run ruff check . --fix --quiet
    @cd react && npm run --silent lint
    @cd python && poetry run ruff check . --quiet
    @cd react && npm run --silent test:unit
    @cd python && poetry run pytest -q

test:
    @cd react && npm test
    @cd python && poetry run pytest

lint:
    @cd react && npm run lint
    @cd python && poetry run ruff check .

format:
    @cd python && poetry run ruff format .

fix:
    @cd python && poetry run ruff check . --fix --unsafe-fixes

discover:
    @node react/scripts/discover.mjs

build:
    @cd react && npm run build
    @cd python && poetry build

publish: ci build
    @echo "Publishing React to npm..."
    @cd react && npm publish
    @echo "Publishing Python to PyPI..."
    @cd python && poetry publish
    @echo "✓ Published to npm and PyPI"

repomix:
    repomix

commits:
    @git --no-pager log --pretty=format:"%h | %ar | %s"
