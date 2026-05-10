#!/bin/bash
set -e

echo "Resetting database..."
rm -f instance/database.db

echo "Starting app to recreate schema..."
python -c "from app import create_app; create_app()"

echo "Seeding data..."
python seed.py
python seed_messages.py

echo "Starting app..."
python app.py
