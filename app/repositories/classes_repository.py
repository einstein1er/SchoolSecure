from app.database.db_connection import get_connection


def creer_classe(nom: str, niveau: str, annee_scolaire: str) -> int:
    connexion = get_connection()
    try:
        curseur = connexion.execute(
            "INSERT INTO classes (nom, niveau, annee_scolaire) VALUES (?, ?, ?)",
            (nom, niveau, annee_scolaire),
        )
        connexion.commit()
        return curseur.lastrowid
    finally:
        connexion.close()


def lister_classes(annee_scolaire: str = None) -> list[dict]:
    connexion = get_connection()
    try:
        if annee_scolaire:
            curseur = connexion.execute(
                "SELECT * FROM classes WHERE annee_scolaire = ? ORDER BY nom",
                (annee_scolaire,),
            )
        else:
            curseur = connexion.execute("SELECT * FROM classes ORDER BY nom")
        return [dict(ligne) for ligne in curseur.fetchall()]
    finally:
        connexion.close()


def obtenir_classe(classe_id: int) -> dict | None:
    connexion = get_connection()
    try:
        curseur = connexion.execute("SELECT * FROM classes WHERE id = ?", (classe_id,))
        ligne = curseur.fetchone()
        return dict(ligne) if ligne else None
    finally:
        connexion.close()
