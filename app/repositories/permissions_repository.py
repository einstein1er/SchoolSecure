"""
Systeme generique de permissions configurables par role.

Principe : chaque permission est identifiee par une cle (string) et
peut etre activee/desactivee independamment pour chaque role, par le
directeur, via l'ecran Gestion des permissions. super_admin a TOUJOURS
acces a tout, quoi qu'il arrive -- non configurable, pour garantir un
acces de secours permanent.

Pour ajouter une nouvelle permission plus tard : l'ajouter a la liste
PERMISSIONS_DISPONIBLES ci-dessous (avec un libelle clair), et appeler
autorise(role, 'ma_nouvelle_cle') a l'endroit du code concerne. Aucune
autre modification necessaire : l'ecran de gestion et la base de
donnees s'adaptent automatiquement a la liste.
"""

from app.database.db_connection import get_connection

# (cle technique, libelle affiche dans l'ecran de gestion des permissions)
PERMISSIONS_DISPONIBLES = [
    ("voir_infos_parent", "Voir les coordonnees du parent d'un eleve"),
    ("eleves_modifier", "Ajouter / modifier un eleve"),
    ("tableau_bord_admin", "Acceder au tableau de bord administratif"),
    ("rh_acces", "Acceder au module Ressources Humaines"),
]

ROLES_CONCERNES = ["secretariat", "comptabilite", "rh", "professeur"]


def autorise(role: str, cle: str) -> bool:
    """Fonction generique : le role a-t-il cette permission ?"""
    if role == "super_admin":
        return True
    connexion = get_connection()
    try:
        curseur = connexion.execute(
            "SELECT autorise FROM permissions WHERE role = ? AND cle = ?", (role, cle)
        )
        ligne = curseur.fetchone()
        return bool(ligne["autorise"]) if ligne else False
    finally:
        connexion.close()


def obtenir_toutes_permissions() -> dict:
    """Retourne {(role, cle): bool} pour toutes les permissions en base."""
    connexion = get_connection()
    try:
        curseur = connexion.execute("SELECT role, cle, autorise FROM permissions")
        return {(l["role"], l["cle"]): bool(l["autorise"]) for l in curseur.fetchall()}
    finally:
        connexion.close()


def definir_permission(role: str, cle: str, valeur: bool) -> None:
    if role == "super_admin":
        return  # non modifiable, toujours vrai de toute facon
    connexion = get_connection()
    try:
        connexion.execute(
            "INSERT INTO permissions (role, cle, autorise) VALUES (?, ?, ?) "
            "ON CONFLICT(role, cle) DO UPDATE SET autorise = excluded.autorise",
            (role, cle, 1 if valeur else 0),
        )
        connexion.commit()
    finally:
        connexion.close()
