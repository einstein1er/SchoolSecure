"""
Fenetre principale - version provisoire.
Pour l'instant elle affiche juste qui est connecte et avec quel role,
histoire de valider que le flux connexion -> redirection fonctionne.
Les vrais ecrans (liste eleves, dashboard, etc.) viendront se greffer
ici aux prochaines etapes, avec un menu qui change selon le role.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal, Qt

NOMS_ROLES = {
    "super_admin": "Super Administrateur (Directeur)",
    "secretariat": "Secretariat",
    "comptabilite": "Comptabilite",
    "rh": "Ressources Humaines",
    "professeur": "Professeur",
    "eleve": "Eleve",
    "parent": "Parent",
}


class MainWindow(QWidget):
    deconnexion_demandee = Signal()

    def __init__(self, utilisateur: dict):
        super().__init__()
        self.utilisateur = utilisateur
        self.setWindowTitle("Gestion Scolaire")
        self.setMinimumSize(600, 400)
        self._construire_interface()

    def _construire_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(12)

        nom_role = NOMS_ROLES.get(self.utilisateur["role"], self.utilisateur["role"])

        bienvenue = QLabel(f"Bienvenue, {self.utilisateur['nom_complet']}")
        bienvenue.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(bienvenue)

        role_label = QLabel(f"Role : {nom_role}")
        layout.addWidget(role_label)

        info = QLabel(
            "Cet ecran est provisoire. Les vrais menus et ecrans "
            "(liste des eleves, paiements, tableau de bord, etc.) "
            "seront ajoutes ici selon le role."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #555;")
        layout.addWidget(info)

        layout.addStretch()

        bouton_deconnexion = QPushButton("Se deconnecter")
        bouton_deconnexion.clicked.connect(self.deconnexion_demandee.emit)
        layout.addWidget(bouton_deconnexion)
