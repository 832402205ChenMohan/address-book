"""SQLite connection helpers and schema definition."""

from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "addressbook.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS contacts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    company     TEXT    NOT NULL DEFAULT '',
    title       TEXT    NOT NULL DEFAULT '',
    notes       TEXT    NOT NULL DEFAULT '',
    is_favorite INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contact_methods (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id  INTEGER NOT NULL,
    kind        TEXT    NOT NULL,
    label       TEXT    NOT NULL DEFAULT '',
    value       TEXT    NOT NULL,
    sort_order  INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (contact_id) REFERENCES contacts (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_methods_contact ON contact_methods (contact_id);
CREATE INDEX IF NOT EXISTS idx_contacts_favorite ON contacts (is_favorite);
"""


def connect(db_path=None):
    """Open a connection to the address book database."""
    path = Path(db_path or DEFAULT_DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(db_path=None):
    """Create the tables when they do not exist yet."""
    connection = connect(db_path)
    try:
        with connection:
            connection.executescript(SCHEMA_SQL)
    finally:
        connection.close()
