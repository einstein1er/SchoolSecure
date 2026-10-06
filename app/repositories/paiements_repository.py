from datetime import datetime
from app.database.db_connection import get_connection
from app.security.crypto_utils import chiffrer, dechiffrer
from app.business.soldes import calculer_solde, valider_montant_paiement
from app.business.numero_recu import generer_numero_recu
from app.business.hash_verification import generer_hash_verification
from app.repositories.eleves_repository import obtenir_eleve
from app.repositories import audit_log_repository

MODES_VALIDES = {"especes", "cheque", "virement", "mobile_money"}


def lister_paiements_eleve(eleve_id: int) -> list[dict]:
    connexion = get_connection()
    try:
        curseur = connexion.execute(
            "SELECT * FROM paiements WHERE eleve_id = ? ORDER BY date_paiement, id",
            (eleve_id,),
        )
        return [_dechiffrer_paiement(ligne) for ligne in curseur.fetchall()]
    finally:
        connexion.close()


def _solde_actuel(eleve_id: int) -> float:
    eleve = obtenir_eleve(eleve_id)
    if eleve is None:
        raise ValueError(f"Eleve {eleve_id} introuvable.")
    paiements = lister_paiements_eleve(eleve_id)
    total_paye = sum(p["montant"] for p in paiements)
    return calculer_solde(eleve["total_du"], [total_paye])


def enregistrer_paiement(eleve_id: int, montant: float, mode_paiement: str, enregistre_par: int,
                          date_paiement: str = None) -> dict:
    """Enregistre un paiement apres validation metier.
    Leve MontantInvalideError si le montant est invalide (via soldes.py).
    Retourne le paiement cree (dechiffre), pret a etre utilise pour
    generer le recu PDF."""
    if mode_paiement not in MODES_VALIDES:
        raise ValueError(f"Mode de paiement invalide : {mode_paiement}")

    date_paiement = date_paiement or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    solde_avant = _solde_actuel(eleve_id)
    valider_montant_paiement(montant, solde_avant)  # leve une exception si invalide
    solde_apres = round(solde_avant - montant, 2)

    numero_recu = generer_numero_recu()
    qr_hash = generer_hash_verification(numero_recu, eleve_id, montant, date_paiement)

    connexion = get_connection()
    try:
        curseur = connexion.execute(
            """INSERT INTO paiements
               (eleve_id, montant_chiffre, date_paiement, mode_paiement,
                numero_recu, solde_apres_chiffre, qr_hash, enregistre_par)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                eleve_id, chiffrer(str(montant)), date_paiement, mode_paiement,
                numero_recu, chiffrer(str(solde_apres)), qr_hash, enregistre_par,
            ),
        )
        connexion.commit()
        paiement_id = curseur.lastrowid
    finally:
        connexion.close()

    audit_log_repository.enregistrer(
        enregistre_par, "CREATION", "paiements", paiement_id,
        f"Paiement {numero_recu} de {montant:.0f} FCFA pour eleve id={eleve_id}"
    )

    return {
        "id": paiement_id,
        "eleve_id": eleve_id,
        "montant": montant,
        "date_paiement": date_paiement,
        "mode_paiement": mode_paiement,
        "numero_recu": numero_recu,
        "solde_apres": solde_apres,
        "qr_hash": qr_hash,
    }


def obtenir_paiement_par_numero(numero_recu: str) -> dict | None:
    """Utile pour reimprimer un recu deja emis depuis l'historique."""
    connexion = get_connection()
    try:
        curseur = connexion.execute("SELECT * FROM paiements WHERE numero_recu = ?", (numero_recu,))
        ligne = curseur.fetchone()
        return _dechiffrer_paiement(ligne) if ligne else None
    finally:
        connexion.close()


def _dechiffrer_paiement(ligne) -> dict:
    d = dict(ligne)
    d["montant"] = float(dechiffrer(d.pop("montant_chiffre")))
    d["solde_apres"] = float(dechiffrer(d.pop("solde_apres_chiffre")))
    return d
