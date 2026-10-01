"""
Regle metier : numero de recu unique, sequentiel, lisible.
Format retenu : REC-<annee>-<compteur sur 6 chiffres>
Exemple : REC-2026-000001, REC-2026-000002, ...
"""

from datetime import datetime
from app.database.db_connection import get_connection


def generer_numero_recu() -> str:
    annee = datetime.now().year
    connexion = get_connection()
    try:
        curseur = connexion.execute(
            "SELECT COUNT(*) AS total FROM paiements WHERE numero_recu LIKE ?",
            (f"REC-{annee}-%",),
        )
        total_existant = curseur.fetchone()["total"]
        nouveau_compteur = total_existant + 1
        return f"REC-{annee}-{nouveau_compteur:06d}"
    finally:
        connexion.close()
