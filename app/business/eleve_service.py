"""
Sert a fabriquer la "fiche complete" d'un eleve pour l'interface :
infos + solde + statut, prets a afficher, sans que l'UI ait a
connaitre le detail du calcul.
"""

from app.repositories.eleves_repository import obtenir_eleve, lister_eleves
from app.repositories.paiements_repository import lister_paiements_eleve
from app.business.soldes import calculer_solde, determiner_statut_complet


def fiche_complete_eleve(eleve_id: int) -> dict | None:
    eleve = obtenir_eleve(eleve_id)
    if eleve is None:
        return None
    paiements = lister_paiements_eleve(eleve_id)
    total_paye = sum(p["montant"] for p in paiements)
    solde = calculer_solde(eleve["total_du"], [total_paye])
    statut = determiner_statut_complet(eleve["total_du"], solde)

    eleve["total_paye"] = round(total_paye, 2)
    eleve["solde"] = solde
    eleve["statut"] = statut
    eleve["paiements"] = paiements
    return eleve


def liste_eleves_avec_statut(classe_id: int = None, recherche: str = None) -> list[dict]:
    """Version allegee (sans re-charger tout l'historique des paiements)
    pour l'ecran liste + tableau de bord."""
    eleves = lister_eleves(classe_id=classe_id, recherche=recherche)
    resultat = []
    for eleve in eleves:
        paiements = lister_paiements_eleve(eleve["id"])
        total_paye = sum(p["montant"] for p in paiements)
        solde = calculer_solde(eleve["total_du"], [total_paye])
        eleve["total_paye"] = round(total_paye, 2)
        eleve["solde"] = solde
        eleve["statut"] = determiner_statut_complet(eleve["total_du"], solde)
        resultat.append(eleve)
    return resultat
