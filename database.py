import sqlite3
import click
from flask import current_app, g


def get_db():
    """Open a database connection, reusing it within the same request."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row  # Rows behave like dicts
    return g.db


def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create tables from schema.sql if they don't exist."""
    import os
    os.makedirs(os.path.dirname(current_app.config["DATABASE"]), exist_ok=True)
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))
