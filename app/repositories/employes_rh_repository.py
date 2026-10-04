from app.database.db_connection import get_connection
from app.security.crypto_utils import dechiffrer


def ajouter_employe(user_id: int, poste: str, departement: str, date_embauche: str = None) -> int:
    connexion = get_connection()
    try:
        curseur = connexion.execute(
            "INSERT INTO employes_rh (user_id, poste, departement, date_embauche) VALUES (?, ?, ?, ?)",
            (user_id, poste, departement, date_embauche),
        )
        connexion.commit()
        return curseur.lastrowid
    finally:
        connexion.close()


def lister_employes() -> list[dict]:
    """Jointure avec users pour recuperer nom_complet (dechiffre) et role."""
    connexion = get_connection()
    try:
        curseur = connexion.execute(
            """SELECT e.id, e.poste, e.departement, e.date_embauche,
                      u.id as user_id, u.username, u.role, u.nom_complet_chiffre
               FROM employes_rh e
               JOIN users u ON u.id = e.user_id
               ORDER BY e.id"""
        )
        resultat = []
        for ligne in curseur.fetchall():
            d = dict(ligne)
            d["nom_complet"] = dechiffrer(d.pop("nom_complet_chiffre"))
            resultat.append(d)
        return resultat
    finally:
        connexion.close()
