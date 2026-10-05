from app.database.db_connection import get_connection


def ajouter_cours(professeur_id: int, classe_id: int, titre: str, description: str, fichier_pdf: str) -> int:
    connexion = get_connection()
    try:
        curseur = connexion.execute(
            """INSERT INTO cours (professeur_id, classe_id, titre, description, fichier_pdf)
               VALUES (?, ?, ?, ?, ?)""",
            (professeur_id, classe_id, titre, description, fichier_pdf),
        )
        connexion.commit()
        return curseur.lastrowid
    finally:
        connexion.close()


def lister_cours_du_professeur(professeur_id: int) -> list[dict]:
    connexion = get_connection()
    try:
        curseur = connexion.execute(
            "SELECT * FROM cours WHERE professeur_id = ? ORDER BY date_creation DESC",
            (professeur_id,),
        )
        return [dict(ligne) for ligne in curseur.fetchall()]
    finally:
        connexion.close()


def lister_cours_par_classe(classe_id: int) -> list[dict]:
    connexion = get_connection()
    try:
        curseur = connexion.execute(
            "SELECT * FROM cours WHERE classe_id = ? ORDER BY date_creation DESC",
            (classe_id,),
        )
        return [dict(ligne) for ligne in curseur.fetchall()]
    finally:
        connexion.close()


def obtenir_cours(cours_id: int) -> dict | None:
    connexion = get_connection()
    try:
        curseur = connexion.execute("SELECT * FROM cours WHERE id = ?", (cours_id,))
        ligne = curseur.fetchone()
        return dict(ligne) if ligne else None
    finally:
        connexion.close()
