"""
Hash de verification pour les recus / QR code.

Principe :
- Le QR code imprime sur le recu est lisible par N'IMPORTE QUEL scanner
  (ca, on ne peut pas l'empecher : un QR code est juste un encodage,
  pas un chiffrement).
- Mais son CONTENU est un hash HMAC calcule avec notre cle secrete.
  Sans cette cle, impossible de regenerer le meme hash : donc seule
  notre application peut verifier qu'un recu est authentique et non
  falsifie (on recalcule le hash a partir des donnees du paiement et
  on compare).
"""

import hmac
import hashlib
from pathlib import Path

CLE_PATH = Path(__file__).resolve().parents[1] / "security" / "secret.key"


def _cle_hmac() -> bytes:
    if not CLE_PATH.exists():
        raise FileNotFoundError(
            "Cle secrete introuvable. Lance d'abord l'initialisation "
            "de la base (init_db.py) qui genere secret.key."
        )
    return CLE_PATH.read_bytes()


def generer_hash_verification(numero_recu: str, eleve_id: int, montant: float, date_paiement: str) -> str:
    """Retourne un hash hexadecimal unique pour ce paiement precis.
    Toute modification d'une seule de ces valeurs change completement
    le hash : ca garantit l'integrite des donnees du recu."""
    message = f"{numero_recu}|{eleve_id}|{montant:.2f}|{date_paiement}"
    signature = hmac.new(_cle_hmac(), message.encode("utf-8"), hashlib.sha256)
    return signature.hexdigest()


def verifier_hash(numero_recu: str, eleve_id: int, montant: float, date_paiement: str, hash_a_verifier: str) -> bool:
    """Recalcule le hash attendu et le compare a celui fourni (ex: scanne
    depuis un QR code). Retourne True si le recu est authentique."""
    hash_attendu = generer_hash_verification(numero_recu, eleve_id, montant, date_paiement)
    return hmac.compare_digest(hash_attendu, hash_a_verifier)
