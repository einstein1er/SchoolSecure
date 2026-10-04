from app.database.db_connection import get_connection


def lier_parent_eleve(parent_user_id: int, eleve_id: int) -> None:
    """Associe un compte parent a un eleve (son enfant). Un parent peut
    avoir plusieurs enfants lies (plusieurs appels de cette fonction)."""
    connexion = get_connection()
    try:
        connexion.execute(
            "INSERT OR IGNORE INTO parents_eleves (parent_user_id, eleve_id) VALUES (?, ?)",
            (parent_user_id, eleve_id),
        )
        connexion.commit()
    finally:
        connexion.close()


def lister_enfants_ids(parent_user_id: int) -> list[int]:
    """Retourne la liste des id d'eleves lies a ce compte parent."""
    connexion = get_connection()
    try:
        curseur = connexion.execute(
            "SELECT eleve_id FROM parents_eleves WHERE parent_user_id = ?", (parent_user_id,)
        )
        return [ligne["eleve_id"] for ligne in curseur.fetchall()]
    finally:
        connexion.close()
