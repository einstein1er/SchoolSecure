"""
Point d'entree unique pour obtenir une connexion a la base.
Toutes les repositories passent par ici, jamais par sqlite3.connect()
directement : ca centralise la configuration (foreign_keys, row_factory).
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "school.db"


def get_connection() -> sqlite3.Connection:
    connexion = sqlite3.connect(DB_PATH)
    connexion.execute("PRAGMA foreign_keys = ON;")
    connexion.row_factory = sqlite3.Row  # permet d'acceder aux colonnes par nom
    return connexion
