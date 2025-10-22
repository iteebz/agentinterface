default:
    @just --list

clean:
    @echo "Cleaning agentinterface..."
    @rm -rf dist build .pytest_cache .ruff_cache __pycache__ node_modules
    @find . -type d -name "__pycache__" -exec rm -rf {} +
    @cd python && rm -rf dist build .pytest_cache .ruff_cache .venv

install:
    @npm install
    @cd python && poetry lock
    @cd python && poetry install

ci:
    @npm run lint:fix || true
    @npm run format || true
    @cd python && poetry run ruff format .
    @cd python && poetry run ruff check . --fix
    @npm run lint
    @cd python && poetry run ruff check .
    @just test
    @just discover

test:
    @npm test
    @cd python && poetry run pytest -v

lint:
    @npm run lint
    @cd python && poetry run ruff check .

format:
    @cd python && poetry run ruff format .

fix:
    @cd python && poetry run ruff check . --fix --unsafe-fixes

discover:
    @npx agentinterface discover

build:
    @npm run build
    @cd python && poetry build

publish: ci build
    @echo "Publishing to npm..."
    @npm publish
    @echo "Publishing to PyPI..."
    @cd python && poetry publish
    @echo "✓ Published to npm and PyPI"

commits:
    @git --no-pager log --pretty=format:"%h | %ar | %s"
