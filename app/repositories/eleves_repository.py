from app.database.db_connection import get_connection
from app.security.crypto_utils import chiffrer, dechiffrer
from app.business.matricule import generer_matricule
from app.repositories import audit_log_repository


def ajouter_eleve(nom: str, prenom: str, classe_id: int, annee_scolaire: str, total_du: float,
                   date_naissance: str = None, sexe: str = None,
                   nom_parent: str = None, telephone_parent: str = None,
                   modifie_par: int = None) -> int:
    matricule = generer_matricule()
    connexion = get_connection()
    try:
        curseur = connexion.execute(
            """INSERT INTO eleves
               (matricule, nom_chiffre, prenom_chiffre, classe_id, annee_scolaire, total_du_chiffre,
                date_naissance, sexe, nom_parent_chiffre, telephone_parent_chiffre)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                matricule, chiffrer(nom), chiffrer(prenom), classe_id, annee_scolaire, chiffrer(str(total_du)),
                date_naissance, sexe,
                chiffrer(nom_parent) if nom_parent else None,
                chiffrer(telephone_parent) if telephone_parent else None,
            ),
        )
        connexion.commit()
        eleve_id = curseur.lastrowid
    finally:
        connexion.close()

    if modifie_par is not None:
        audit_log_repository.enregistrer(
            modifie_par, "CREATION", "eleves", eleve_id, f"Creation eleve {matricule} ({prenom} {nom})"
        )
    return eleve_id


def modifier_eleve(eleve_id: int, nom: str = None, prenom: str = None,
                    classe_id: int = None, total_du: float = None,
                    date_naissance: str = None, sexe: str = None,
                    nom_parent: str = None, telephone_parent: str = None,
                    modifier_champs_parent: bool = False,
                    modifie_par: int = None) -> None:
    """modifier_champs_parent : si False (par defaut), les champs nom_parent/
    telephone_parent ne sont PAS touches, meme si on passe None -- protege
    les donnees restreintes contre un ecrasement accidentel par un role qui
    ne les voit pas dans son formulaire. Passer True explicitement (ex:
    depuis le formulaire ouvert par le directeur) pour vraiment les modifier."""
    eleve_actuel = obtenir_eleve(eleve_id)
    if eleve_actuel is None:
        raise ValueError(f"Eleve {eleve_id} introuvable.")

    nom = nom if nom is not None else eleve_actuel["nom"]
    prenom = prenom if prenom is not None else eleve_actuel["prenom"]
    classe_id = classe_id if classe_id is not None else eleve_actuel["classe_id"]
    total_du = total_du if total_du is not None else eleve_actuel["total_du"]
    date_naissance = date_naissance if date_naissance is not None else eleve_actuel.get("date_naissance")
    sexe = sexe if sexe is not None else eleve_actuel.get("sexe")

    connexion = get_connection()
    try:
        if modifier_champs_parent:
            connexion.execute(
                """UPDATE eleves SET nom_chiffre = ?, prenom_chiffre = ?, classe_id = ?, total_du_chiffre = ?,
                   date_naissance = ?, sexe = ?, nom_parent_chiffre = ?, telephone_parent_chiffre = ?
                   WHERE id = ?""",
                (
                    chiffrer(nom), chiffrer(prenom), classe_id, chiffrer(str(total_du)),
                    date_naissance, sexe,
                    chiffrer(nom_parent) if nom_parent else None,
                    chiffrer(telephone_parent) if telephone_parent else None,
                    eleve_id,
                ),
            )
        else:
            connexion.execute(
                """UPDATE eleves SET nom_chiffre = ?, prenom_chiffre = ?, classe_id = ?, total_du_chiffre = ?,
                   date_naissance = ?, sexe = ?
                   WHERE id = ?""",
                (chiffrer(nom), chiffrer(prenom), classe_id, chiffrer(str(total_du)), date_naissance, sexe, eleve_id),
            )
        connexion.commit()
    finally:
        connexion.close()

    if modifie_par is not None:
        audit_log_repository.enregistrer(
            modifie_par, "MODIFICATION", "eleves", eleve_id,
            f"Modification eleve {eleve_actuel['matricule']} ({prenom} {nom})"
        )


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


def obtenir_eleve_par_user_id(user_id: int) -> dict | None:
    """Retrouve la fiche eleve liee a un compte de connexion donne.
    Utilise pour le dashboard eleve : l'eleve connecte voit SA fiche."""
    connexion = get_connection()
    try:
        curseur = connexion.execute("SELECT * FROM eleves WHERE user_id = ?", (user_id,))
        ligne = curseur.fetchone()
        return _dechiffrer_eleve(ligne) if ligne else None
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
    nom_parent_chiffre = d.pop("nom_parent_chiffre", None)
    telephone_parent_chiffre = d.pop("telephone_parent_chiffre", None)
    d["nom_parent"] = dechiffrer(nom_parent_chiffre) if nom_parent_chiffre else None
    d["telephone_parent"] = dechiffrer(telephone_parent_chiffre) if telephone_parent_chiffre else None
    return d
