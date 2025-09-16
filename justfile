default:
    @just --list

install:
    @npm install
    @cd python && poetry install

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
    @cd python && poetry build

publish: ci build
    @cd python && poetry publish

clean:
    @rm -rf dist build .pytest_cache .ruff_cache __pycache__ node_modules
    @find . -type d -name "__pycache__" -exec rm -rf {} +
    @cd python && rm -rf dist build .pytest_cache .ruff_cache .venv

commits:
    @git --no-pager log --pretty=format:"%ar %s"

ci: format fix lint test discover
