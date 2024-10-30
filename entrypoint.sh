#!/bin/bash

# Set the PYTHONPATH
export PYTHONPATH=.

# Run migrations
pipenv run alembic upgrade head

# Create initial data in DB
pipenv run python -m app.initialiser

# Start the FastAPI application
exec pipenv run python -m app.main
