from app.database.db_connection import get_connection
from app.security.crypto_utils import dechiffrer


def enregistrer(user_id: int, action: str, table_concernee: str,
                 enregistrement_id: int = None, details: str = None) -> None:
    """N'echoue jamais bruyamment : le journal d'audit ne doit pas
    empecher l'action principale de fonctionner si la journalisation
    pose probleme. On avale l'exception en dernier recours."""
    try:
        connexion = get_connection()
        try:
            connexion.execute(
                """INSERT INTO audit_log (user_id, action, table_concernee, enregistrement_id, details)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, action, table_concernee, enregistrement_id, details),
            )
            connexion.commit()
        finally:
            connexion.close()
    except Exception:
        pass


def lister(limite: int = 300) -> list[dict]:
    connexion = get_connection()
    try:
        curseur = connexion.execute(
            """SELECT a.*, u.nom_complet_chiffre, u.role
               FROM audit_log a
               LEFT JOIN users u ON u.id = a.user_id
               ORDER BY a.date_action DESC
               LIMIT ?""",
            (limite,),
        )
        resultat = []
        for ligne in curseur.fetchall():
            d = dict(ligne)
            nom_chiffre = d.pop("nom_complet_chiffre", None)
            d["nom_utilisateur"] = dechiffrer(nom_chiffre) if nom_chiffre else "(compte supprime)"
            resultat.append(d)
        return resultat
    finally:
        connexion.close()
