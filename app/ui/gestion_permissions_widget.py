"""
Ecran generique de gestion des permissions, reserve au super_admin.
Affiche une grille Role x Permission (cases a cocher), sauvegardee en
base, lue dynamiquement partout ailleurs dans l'application. Pour
ajouter une nouvelle permission plus tard, il suffit de l'ajouter a
PERMISSIONS_DISPONIBLES dans permissions_repository.py -- cet ecran
s'adapte automatiquement, sans aucune autre modification necessaire.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QCheckBox,
    QPushButton, QFrame, QMessageBox, QScrollArea
)

from app.repositories import permissions_repository, audit_log_repository

NOMS_ROLES = {
    "secretariat": "Secretariat",
    "comptabilite": "Comptabilite",
    "rh": "Ressources Humaines",
    "professeur": "Professeur",
}


class GestionPermissionsWidget(QWidget):
    def __init__(self, utilisateur_id: int = None):
        super().__init__()
        self.utilisateur_id = utilisateur_id
        self.cases = {}  # {(role, cle): QCheckBox}
        self._construire_interface()
        self._charger()

    def _construire_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        titre = QLabel("Gestion des permissions")
        titre.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(titre)

        note = QLabel(
            "Le Super Administrateur a toujours acces a tout et n'apparait pas "
            "dans cette liste. Cochez les permissions a accorder a chaque role, "
            "puis cliquez sur Enregistrer. Les changements sont effectifs "
            "immediatement pour les utilisateurs concernes."
        )
        note.setStyleSheet("color: #666;")
        note.setWordWrap(True)
        layout.addWidget(note)

        zone_defilement = QScrollArea()
        zone_defilement.setWidgetResizable(True)
        cadre = QFrame()
        cadre.setStyleSheet("QFrame { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; }")
        grille = QGridLayout(cadre)
        grille.setContentsMargins(16, 16, 16, 16)
        grille.setHorizontalSpacing(24)
        grille.setVerticalSpacing(12)

        # En-tete : une colonne par permission
        label_role_entete = QLabel("Role")
        label_role_entete.setStyleSheet("font-weight: bold; color: #444;")
        grille.addWidget(label_role_entete, 0, 0)

        for col, (cle, libelle) in enumerate(permissions_repository.PERMISSIONS_DISPONIBLES, start=1):
            label = QLabel(libelle)
            label.setStyleSheet("font-weight: bold; color: #444;")
            label.setWordWrap(True)
            label.setFixedWidth(180)
            grille.addWidget(label, 0, col)

        ligne_separation = QFrame()
        ligne_separation.setFrameShape(QFrame.HLine)
        ligne_separation.setStyleSheet("color: #cbd5e1;")
        grille.addWidget(ligne_separation, 1, 0, 1, len(permissions_repository.PERMISSIONS_DISPONIBLES) + 1)

        # Une ligne par role
        for row, role in enumerate(permissions_repository.ROLES_CONCERNES, start=2):
            label_role = QLabel(NOMS_ROLES.get(role, role))
            grille.addWidget(label_role, row, 0)

            for col, (cle, libelle) in enumerate(permissions_repository.PERMISSIONS_DISPONIBLES, start=1):
                case = QCheckBox()
                self.cases[(role, cle)] = case
                grille.addWidget(case, row, col)

        zone_defilement.setWidget(cadre)
        layout.addWidget(zone_defilement)

        boutons = QHBoxLayout()
        bouton_actualiser = QPushButton("Actualiser")
        bouton_actualiser.clicked.connect(self._charger)
        boutons.addWidget(bouton_actualiser)

        bouton_enregistrer = QPushButton("Enregistrer")
        bouton_enregistrer.setStyleSheet(
            "background-color: #2563eb; color: white; font-weight: bold; padding: 6px 14px;"
        )
        bouton_enregistrer.clicked.connect(self._enregistrer)
        boutons.addWidget(bouton_enregistrer)
        boutons.addStretch()

        layout.addLayout(boutons)

    def _charger(self):
        valeurs = permissions_repository.obtenir_toutes_permissions()
        for (role, cle), case in self.cases.items():
            case.setChecked(valeurs.get((role, cle), False))

    def _enregistrer(self):
        for (role, cle), case in self.cases.items():
            permissions_repository.definir_permission(role, cle, case.isChecked())
        if self.utilisateur_id is not None:
            audit_log_repository.enregistrer(
                self.utilisateur_id, "MODIFICATION", "permissions", None,
                "Mise a jour de la grille des permissions par role"
            )
        QMessageBox.information(
            self, "Permissions enregistrees",
            "Les permissions ont ete mises a jour. Elles seront appliquees "
            "des la prochaine ouverture de l'ecran concerne par chaque "
            "utilisateur."
        )
