"""
Sert les donnees necessaires au dashboard professeur.
Principe de cloisonnement : un professeur voit la liste de ses eleves
(nom, prenom, classe) mais JAMAIS leurs informations financieres
(total du, solde, statut de paiement) -- ce n'est pas son role.
"""

from app.repositories import professeurs_repository, eleves_repository, classes_repository


def lister_eleves_du_professeur(user_id: int) -> list[dict]:
    """Retourne la liste des eleves des classes assignees a ce professeur,
    avec UNIQUEMENT des champs pedagogiques (pas de montants)."""
    professeur = professeurs_repository.obtenir_professeur_par_user_id(user_id)
    if professeur is None:
        return []

    classes = professeurs_repository.lister_classes_du_professeur(professeur["id"])
    resultat = []
    for classe in classes:
        eleves_de_la_classe = eleves_repository.lister_eleves(classe_id=classe["id"])
        for e in eleves_de_la_classe:
            resultat.append({
                "matricule": e["matricule"],
                "nom": e["nom"],
                "prenom": e["prenom"],
                "classe_nom": classe["nom"],
            })
    return resultat


def lister_classes_du_professeur(user_id: int) -> list[dict]:
    professeur = professeurs_repository.obtenir_professeur_par_user_id(user_id)
    if professeur is None:
        return []
    return professeurs_repository.lister_classes_du_professeur(professeur["id"])
