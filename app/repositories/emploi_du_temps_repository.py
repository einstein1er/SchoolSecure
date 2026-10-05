from app.database.db_connection import get_connection

JOURS_VALIDES = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]


def ajouter_creneau(professeur_id: int, classe_id: int, jour: str, heure_debut: str, heure_fin: str, matiere: str) -> int:
    if jour not in JOURS_VALIDES:
        raise ValueError(f"Jour invalide : {jour}")
    connexion = get_connection()
    try:
        curseur = connexion.execute(
            """INSERT INTO emploi_du_temps (professeur_id, classe_id, jour, heure_debut, heure_fin, matiere)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (professeur_id, classe_id, jour, heure_debut, heure_fin, matiere),
        )
        connexion.commit()
        return curseur.lastrowid
    finally:
        connexion.close()


def lister_creneaux_du_professeur(professeur_id: int) -> list[dict]:
    connexion = get_connection()
    try:
        curseur = connexion.execute(
            "SELECT * FROM emploi_du_temps WHERE professeur_id = ? ORDER BY "
            "CASE jour WHEN 'lundi' THEN 1 WHEN 'mardi' THEN 2 WHEN 'mercredi' THEN 3 "
            "WHEN 'jeudi' THEN 4 WHEN 'vendredi' THEN 5 WHEN 'samedi' THEN 6 END, heure_debut",
            (professeur_id,),
        )
        return [dict(ligne) for ligne in curseur.fetchall()]
    finally:
        connexion.close()


def lister_creneaux_par_classe(classe_id: int) -> list[dict]:
    connexion = get_connection()
    try:
        curseur = connexion.execute(
            "SELECT * FROM emploi_du_temps WHERE classe_id = ? ORDER BY "
            "CASE jour WHEN 'lundi' THEN 1 WHEN 'mardi' THEN 2 WHEN 'mercredi' THEN 3 "
            "WHEN 'jeudi' THEN 4 WHEN 'vendredi' THEN 5 WHEN 'samedi' THEN 6 END, heure_debut",
            (classe_id,),
        )
        return [dict(ligne) for ligne in curseur.fetchall()]
    finally:
        connexion.close()


def supprimer_creneau(creneau_id: int) -> None:
    connexion = get_connection()
    try:
        connexion.execute("DELETE FROM emploi_du_temps WHERE id = ?", (creneau_id,))
        connexion.commit()
    finally:
        connexion.close()
