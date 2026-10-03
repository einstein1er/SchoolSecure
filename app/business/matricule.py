"""
Regle metier : matricule eleve unique, sequentiel, lisible.
Format : ELV-<annee>-<compteur sur 3 chiffres>
Exemple : ELV-2026-001, ELV-2026-002, ...
"""

from datetime import datetime
from app.database.db_connection import get_connection


def generer_matricule() -> str:
    annee = datetime.now().year
    connexion = get_connection()
    try:
        curseur = connexion.execute(
            "SELECT COUNT(*) AS total FROM eleves WHERE matricule LIKE ?",
            (f"ELV-{annee}-%",),
        )
        total_existant = curseur.fetchone()["total"]
        return f"ELV-{annee}-{total_existant + 1:03d}"
    finally:
        connexion.close()
