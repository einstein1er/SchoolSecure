"""
Script d'initialisation de la base de donnees.

Usage (depuis la racine du projet, venv active) :
    python app/database/init_db.py

Ce script :
1. Cree le fichier school.db s'il n'existe pas
2. Execute schema.sql pour creer toutes les tables
3. Prepare aussi la cle de chiffrement si elle n'existe pas encore
"""

import sqlite3
from pathlib import Path
import sys

# Permet d'importer app.security.crypto_utils meme en lancant ce fichier
# directement depuis app/database/
sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.security.crypto_utils import generer_cle_si_absente

DB_PATH = Path(__file__).parent / "school.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def initialiser_base():
    print(f"Base de donnees : {DB_PATH}")
    connexion = sqlite3.connect(DB_PATH)
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            script_sql = f.read()
        connexion.executescript(script_sql)
        connexion.commit()
        print("Toutes les tables ont ete creees avec succes.")
    finally:
        connexion.close()


if __name__ == "__main__":
    generer_cle_si_absente()
    initialiser_base()
