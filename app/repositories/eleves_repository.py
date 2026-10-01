from app.database.db_connection import get_connection
from app.security.crypto_utils import chiffrer, dechiffrer


def ajouter_eleve(nom: str, prenom: str, classe_id: int, annee_scolaire: str, total_du: float) -> int:
    connexion = get_connection()
    try:
        curseur = connexion.execute(
            """INSERT INTO eleves (nom_chiffre, prenom_chiffre, classe_id, annee_scolaire, total_du_chiffre)
               VALUES (?, ?, ?, ?, ?)""",
            (chiffrer(nom), chiffrer(prenom), classe_id, annee_scolaire, chiffrer(str(total_du))),
        )
        connexion.commit()
        return curseur.lastrowid
    finally:
        connexion.close()


def modifier_eleve(eleve_id: int, nom: str = None, prenom: str = None,
                    classe_id: int = None, total_du: float = None) -> None:
    eleve_actuel = obtenir_eleve(eleve_id)
    if eleve_actuel is None:
        raise ValueError(f"Eleve {eleve_id} introuvable.")

    nom = nom if nom is not None else eleve_actuel["nom"]
    prenom = prenom if prenom is not None else eleve_actuel["prenom"]
    classe_id = classe_id if classe_id is not None else eleve_actuel["classe_id"]
    total_du = total_du if total_du is not None else eleve_actuel["total_du"]

    connexion = get_connection()
    try:
        connexion.execute(
            """UPDATE eleves SET nom_chiffre = ?, prenom_chiffre = ?, classe_id = ?, total_du_chiffre = ?
               WHERE id = ?""",
            (chiffrer(nom), chiffrer(prenom), classe_id, chiffrer(str(total_du)), eleve_id),
        )
        connexion.commit()
    finally:
        connexion.close()


def associer_compte_utilisateur(eleve_id: int, user_id: int) -> None:
    """Relie un eleve a son compte de connexion (role 'eleve' dans users).
    Permet ensuite a l'eleve de se connecter et voir son dashboard."""
    connexion = get_connection()
    try:
        connexion.execute("UPDATE eleves SET user_id = ? WHERE id = ?", (user_id, eleve_id))
        connexion.commit()
    finally:
        connexion.close()


def supprimer_eleve(eleve_id: int) -> None:
    connexion = get_connection()
    try:
        connexion.execute("DELETE FROM eleves WHERE id = ?", (eleve_id,))
        connexion.commit()
    finally:
        connexion.close()


def obtenir_eleve(eleve_id: int) -> dict | None:
    connexion = get_connection()
    try:
        curseur = connexion.execute("SELECT * FROM eleves WHERE id = ?", (eleve_id,))
        ligne = curseur.fetchone()
        return _dechiffrer_eleve(ligne) if ligne else None
    finally:
        connexion.close()


def lister_eleves(classe_id: int = None, recherche: str = None) -> list[dict]:
    """Filtre par classe cote SQL (colonne en clair, rapide).
    Le filtre par texte de recherche (nom/prenom) se fait APRES
    dechiffrement, en Python, puisque ces colonnes sont chiffrees et
    ne peuvent pas etre cherchees directement en SQL."""
    connexion = get_connection()
    try:
        if classe_id:
            curseur = connexion.execute("SELECT * FROM eleves WHERE classe_id = ?", (classe_id,))
        else:
            curseur = connexion.execute("SELECT * FROM eleves")
        eleves = [_dechiffrer_eleve(ligne) for ligne in curseur.fetchall()]
    finally:
        connexion.close()

    if recherche:
        recherche_minuscule = recherche.lower()
        eleves = [
            e for e in eleves
            if recherche_minuscule in e["nom"].lower() or recherche_minuscule in e["prenom"].lower()
        ]
    return eleves


def _dechiffrer_eleve(ligne) -> dict:
    d = dict(ligne)
    d["nom"] = dechiffrer(d.pop("nom_chiffre"))
    d["prenom"] = dechiffrer(d.pop("prenom_chiffre"))
    d["total_du"] = float(dechiffrer(d.pop("total_du_chiffre")))
    return d
