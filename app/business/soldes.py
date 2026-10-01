"""
Regles metier autour du solde d'un eleve.
Ce module ne touche jamais directement au SQL : il utilise les
repositories, qui lui rendent des donnees deja dechiffrees.
"""


class MontantInvalideError(Exception):
    """Leve quand un paiement ferait passer le solde sous zero."""
    pass


def calculer_solde(total_du: float, paiements: list[float]) -> float:
    """total_du et paiements sont deja en clair (dechiffres en amont).
    Retourne le solde restant du (jamais negatif dans les faits, mais
    on ne force rien ici : la validation se fait a l'enregistrement)."""
    return round(total_du - sum(paiements), 2)


def determiner_statut(solde: float) -> str:
    if solde <= 0:
        return "Solde"
    return "Non paye"  # affine plus bas si des paiements existent


def determiner_statut_complet(total_du: float, solde: float) -> str:
    """Version complete : distingue 'Non paye' (aucun paiement) de
    'Partiellement paye' (au moins un paiement mais pas complet)."""
    if solde <= 0:
        return "Solde"
    if solde < total_du:
        return "Partiellement paye"
    return "Non paye"


def valider_montant_paiement(montant: float, solde_actuel: float) -> None:
    """Leve MontantInvalideError si le paiement est invalide.
    Regle du brief : un paiement ne doit jamais faire passer le solde
    en dessous de 0."""
    if montant <= 0:
        raise MontantInvalideError("Le montant doit etre superieur a zero.")
    if montant > solde_actuel:
        raise MontantInvalideError(
            f"Le montant saisi ({montant:.2f}) depasse le solde restant "
            f"({solde_actuel:.2f})."
        )
