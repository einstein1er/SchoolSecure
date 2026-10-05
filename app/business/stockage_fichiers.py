"""
Stockage local des fichiers PDF de cours deposes par les professeurs.
Les fichiers sont copies dans un dossier local du projet (jamais sur
Internet, conforme a l'exigence "100% offline"). Seul le CHEMIN
RELATIF est stocke en base -- pas le contenu du fichier lui-meme.
"""

import shutil
import uuid
from pathlib import Path
from datetime import datetime

DOSSIER_COURS = Path(__file__).resolve().parents[2] / "fichiers_cours"


def copier_fichier_cours(chemin_source: str) -> str:
    """Copie le PDF choisi par le professeur dans le dossier local de
    l'application, avec un nom de fichier unique (pour eviter tout
    ecrasement accidentel entre deux cours). Retourne le chemin
    RELATIF (a stocker en base), pas le chemin absolu."""
    DOSSIER_COURS.mkdir(parents=True, exist_ok=True)

    source = Path(chemin_source)
    horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
    identifiant_unique = uuid.uuid4().hex[:8]
    nom_fichier = f"{horodatage}_{identifiant_unique}_{source.name}"

    destination = DOSSIER_COURS / nom_fichier
    shutil.copy2(source, destination)

    return nom_fichier  # chemin relatif au dossier fichiers_cours/


def obtenir_chemin_absolu(nom_fichier: str) -> Path:
    return DOSSIER_COURS / nom_fichier
