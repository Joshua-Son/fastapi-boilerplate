#!/usr/bin/env sh

export PYTHONPATH=.

# Run migrations
pipenv run alembic upgrade head

# Create initial data in DB
pipenv run python -m app.initialiser
