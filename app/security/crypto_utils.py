"""
Module de chiffrement des donnees sensibles.

Principe :
- On genere UNE cle secrete (Fernet), stockee dans un fichier local
  'secret.key', JAMAIS commite dans Git (voir .gitignore).
- Toutes les colonnes "_chiffre" de la base sont chiffrees avec cette
  cle avant ecriture, et dechiffrees apres lecture.
- Si on perd le fichier secret.key, les donnees chiffrees sont
  definitivement illisibles : il faut donc absolument le sauvegarder
  (ex: copie sur cle USB, coffre-fort numerique de l'etablissement).
"""

from pathlib import Path
from cryptography.fernet import Fernet

# Chemin du fichier contenant la cle secrete (a cote de ce module)
KEY_PATH = Path(__file__).parent / "secret.key"


def generer_cle_si_absente() -> None:
    """Cree le fichier secret.key s'il n'existe pas encore.
    A appeler UNE SEULE FOIS au tout premier lancement de l'application
    (ou explicitement lors de l'installation sur un nouveau poste)."""
    if not KEY_PATH.exists():
        cle = Fernet.generate_key()
        KEY_PATH.write_bytes(cle)
        print(f"Nouvelle cle de chiffrement generee : {KEY_PATH}")
    else:
        print("La cle de chiffrement existe deja, rien a faire.")


def _charger_fernet() -> Fernet:
    if not KEY_PATH.exists():
        raise FileNotFoundError(
            "Aucune cle de chiffrement trouvee. "
            "Lance d'abord generer_cle_si_absente()."
        )
    cle = KEY_PATH.read_bytes()
    return Fernet(cle)


def chiffrer(texte_clair: str) -> str:
    """Chiffre une chaine de caracteres et retourne le resultat en texte
    (pret a etre stocke dans une colonne TEXT de SQLite)."""
    if texte_clair is None:
        return None
    f = _charger_fernet()
    return f.encrypt(texte_clair.encode("utf-8")).decode("utf-8")


def dechiffrer(texte_chiffre: str) -> str:
    """Dechiffre une chaine precedemment chiffree avec chiffrer()."""
    if texte_chiffre is None:
        return None
    f = _charger_fernet()
    return f.decrypt(texte_chiffre.encode("utf-8")).decode("utf-8")


if __name__ == "__main__":
    # Petit test manuel : lance "python app/security/crypto_utils.py"
    generer_cle_si_absente()
    exemple = "Kodjo AMEGAN"
    c = chiffrer(exemple)
    d = dechiffrer(c)
    print("Texte original :", exemple)
    print("Texte chiffre  :", c)
    print("Texte dechiffre:", d)
    assert d == exemple, "Erreur : le dechiffrement ne redonne pas le texte original !"
    print("Test reussi.")
