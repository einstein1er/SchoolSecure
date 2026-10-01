"""
Repository des utilisateurs.
Gere la creation de comptes et la verification des identifiants.
Le mot de passe n'est JAMAIS stocke en clair ni meme chiffre de facon
reversible : on utilise bcrypt (hachage a sens unique), la meme
technique que la quasi-totalite des sites web serieux.
"""

import bcrypt
from app.database.db_connection import get_connection
from app.security.crypto_utils import chiffrer, dechiffrer

ROLES_VALIDES = {
    "super_admin", "secretariat", "comptabilite",
    "rh", "professeur", "eleve", "parent",
}


def _hacher_mot_de_passe(mot_de_passe: str) -> str:
    sel = bcrypt.gensalt()
    return bcrypt.hashpw(mot_de_passe.encode("utf-8"), sel).decode("utf-8")


def creer_utilisateur(username: str, mot_de_passe: str, role: str,
                       nom_complet: str, email: str = None, telephone: str = None) -> int:
    if role not in ROLES_VALIDES:
        raise ValueError(f"Role invalide : {role}")

    connexion = get_connection()
    try:
        curseur = connexion.execute(
            """INSERT INTO users
               (username, password_hash, role, nom_complet_chiffre, email_chiffre, telephone_chiffre)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                username,
                _hacher_mot_de_passe(mot_de_passe),
                role,
                chiffrer(nom_complet),
                chiffrer(email) if email else None,
                chiffrer(telephone) if telephone else None,
            ),
        )
        connexion.commit()
        return curseur.lastrowid
    finally:
        connexion.close()


def verifier_identifiants(username: str, mot_de_passe: str) -> dict | None:
    """Retourne l'utilisateur (dechiffre) si le mot de passe est correct
    et le compte actif, sinon None."""
    connexion = get_connection()
    try:
        curseur = connexion.execute(
            "SELECT * FROM users WHERE username = ? AND actif = 1", (username,)
        )
        ligne = curseur.fetchone()
        if ligne is None:
            return None
        if not bcrypt.checkpw(mot_de_passe.encode("utf-8"), ligne["password_hash"].encode("utf-8")):
            return None
        return _dechiffrer_utilisateur(ligne)
    finally:
        connexion.close()


def obtenir_utilisateur(user_id: int) -> dict | None:
    connexion = get_connection()
    try:
        curseur = connexion.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        ligne = curseur.fetchone()
        return _dechiffrer_utilisateur(ligne) if ligne else None
    finally:
        connexion.close()


def lister_utilisateurs_par_role(role: str) -> list[dict]:
    connexion = get_connection()
    try:
        curseur = connexion.execute("SELECT * FROM users WHERE role = ?", (role,))
        return [_dechiffrer_utilisateur(ligne) for ligne in curseur.fetchall()]
    finally:
        connexion.close()


def _dechiffrer_utilisateur(ligne) -> dict:
    d = dict(ligne)
    d["nom_complet"] = dechiffrer(d.pop("nom_complet_chiffre"))
    d["email"] = dechiffrer(d.pop("email_chiffre")) if d.get("email_chiffre") else None
    d["telephone"] = dechiffrer(d.pop("telephone_chiffre")) if d.get("telephone_chiffre") else None
    d.pop("password_hash", None)  # jamais renvoye en dehors de la verification
    return d
