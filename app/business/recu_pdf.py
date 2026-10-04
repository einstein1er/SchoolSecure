"""
Generation du recu de paiement en PDF, avec QR code de verification.

Le QR code encode le hash de verification (genere a l'enregistrement du
paiement, voir hash_verification.py) + le numero de recu : n'importe
quel scanner peut LIRE ce contenu, mais seule cette application peut
le VERIFIER (recalculer le hash attendu et comparer), puisque le hash
depend de la cle secrete de l'etablissement.
"""

import io
import tempfile
from pathlib import Path

from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
import qrcode

from app.repositories import paiements_repository, eleves_repository, classes_repository

NOM_ETABLISSEMENT = "Etablissement Scolaire"  # a rendre configurable plus tard

LIBELLES_MODE_PAIEMENT = {
    "especes": "Especes",
    "cheque": "Cheque",
    "virement": "Virement",
    "mobile_money": "Mobile Money",
}


class RecuIntrouvableError(Exception):
    pass


def generer_pdf_recu(numero_recu: str, chemin_fichier: str) -> str:
    """Genere le PDF du recu identifie par numero_recu et l'ecrit a
    chemin_fichier. Retourne le chemin ecrit. Peut etre appele a
    n'importe quel moment, meme bien apres le paiement (reimpression),
    puisque tout est recalcule a partir des donnees en base."""
    paiement = paiements_repository.obtenir_paiement_par_numero(numero_recu)
    if paiement is None:
        raise RecuIntrouvableError(f"Aucun paiement trouve avec le numero {numero_recu}.")

    eleve = eleves_repository.obtenir_eleve(paiement["eleve_id"])
    classe = classes_repository.obtenir_classe(eleve["classe_id"]) if eleve else None
    nom_classe = classe["nom"] if classe else "?"

    qr_image_bytes = _generer_image_qr(paiement)

    largeur, hauteur = A5
    c = canvas.Canvas(chemin_fichier, pagesize=A5)

    marge = 15 * mm
    y = hauteur - marge

    # --- En-tete ---
    c.setFont("Helvetica-Bold", 16)
    c.drawString(marge, y, NOM_ETABLISSEMENT)
    y -= 8 * mm

    c.setFont("Helvetica-Bold", 13)
    c.drawString(marge, y, "RECU DE PAIEMENT")
    y -= 6 * mm

    c.setFont("Helvetica", 10)
    c.drawString(marge, y, f"N\u00b0 {paiement['numero_recu']}")
    y -= 10 * mm

    c.line(marge, y, largeur - marge, y)
    y -= 8 * mm

    # --- Infos eleve ---
    c.setFont("Helvetica-Bold", 10)
    c.drawString(marge, y, "Eleve")
    y -= 5.5 * mm
    c.setFont("Helvetica", 10)
    c.drawString(marge, y, f"{eleve['prenom']} {eleve['nom']}  (Matricule : {eleve['matricule']})")
    y -= 5.5 * mm
    c.drawString(marge, y, f"Classe : {nom_classe}   Annee scolaire : {eleve['annee_scolaire']}")
    y -= 10 * mm

    # --- Infos paiement ---
    c.setFont("Helvetica-Bold", 10)
    c.drawString(marge, y, "Paiement")
    y -= 5.5 * mm
    c.setFont("Helvetica", 10)
    c.drawString(marge, y, f"Date : {paiement['date_paiement']}")
    y -= 5.5 * mm
    c.drawString(marge, y, f"Mode de paiement : {LIBELLES_MODE_PAIEMENT.get(paiement['mode_paiement'], paiement['mode_paiement'])}")
    y -= 8 * mm

    c.setFont("Helvetica-Bold", 13)
    c.drawString(marge, y, f"Montant paye : {paiement['montant']:,.0f} FCFA".replace(",", " "))
    y -= 7 * mm

    c.setFont("Helvetica-Bold", 11)
    c.drawString(marge, y, f"Solde restant apres ce paiement : {paiement['solde_apres']:,.0f} FCFA".replace(",", " "))
    y -= 12 * mm

    # --- QR code en bas, avec le texte de verification ---
    taille_qr = 30 * mm
    c.drawImage(
        ImageReader(io.BytesIO(qr_image_bytes)), marge, y - taille_qr, width=taille_qr, height=taille_qr,
        preserveAspectRatio=True, mask="auto"
    )
    c.setFont("Helvetica", 7)
    c.drawString(marge + taille_qr + 4 * mm, y - 5 * mm, "Scannez pour verifier l'authenticite")
    c.drawString(marge + taille_qr + 4 * mm, y - 9 * mm, "de ce recu via l'application de")
    c.drawString(marge + taille_qr + 4 * mm, y - 13 * mm, "l'etablissement.")

    c.showPage()
    c.save()
    return chemin_fichier


def _generer_image_qr(paiement: dict) -> bytes:
    """Le QR code contient le numero de recu et le hash de verification,
    separes par '|'. N'importe qui peut le lire (c'est juste du texte
    encode), mais sans la cle secrete de l'etablissement, impossible de
    recalculer/valider ce hash -- donc impossible de fabriquer un faux
    recu credible."""
    contenu = f"{paiement['numero_recu']}|{paiement['qr_hash']}"
    img = qrcode.make(contenu)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
