from app.database.db_connection import get_connection


def creer_professeur(user_id: int, specialite: str = None) -> int:
    connexion = get_connection()
    try:
        curseur = connexion.execute(
            "INSERT INTO professeurs (user_id, specialite) VALUES (?, ?)",
            (user_id, specialite),
        )
        connexion.commit()
        return curseur.lastrowid
    finally:
        connexion.close()


def obtenir_professeur_par_user_id(user_id: int) -> dict | None:
    connexion = get_connection()
    try:
        curseur = connexion.execute("SELECT * FROM professeurs WHERE user_id = ?", (user_id,))
        ligne = curseur.fetchone()
        return dict(ligne) if ligne else None
    finally:
        connexion.close()


def assigner_classe(professeur_id: int, classe_id: int) -> None:
    connexion = get_connection()
    try:
        connexion.execute(
            "INSERT OR IGNORE INTO professeurs_classes (professeur_id, classe_id) VALUES (?, ?)",
            (professeur_id, classe_id),
        )
        connexion.commit()
    finally:
        connexion.close()


def lister_classes_du_professeur(professeur_id: int) -> list[dict]:
    connexion = get_connection()
    try:
        curseur = connexion.execute(
            """SELECT c.* FROM classes c
               JOIN professeurs_classes pc ON pc.classe_id = c.id
               WHERE pc.professeur_id = ?
               ORDER BY c.nom""",
            (professeur_id,),
        )
        return [dict(ligne) for ligne in curseur.fetchall()]
    finally:
        connexion.close()
