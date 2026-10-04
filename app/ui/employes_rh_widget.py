"""
Ecran RH : liste des employes (hors eleves), avec possibilite d'en
ajouter un nouveau (ce qui cree aussi son compte de connexion).
Visible pour super_admin et rh.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton
)

from app.repositories import employes_rh_repository
from app.ui.employe_form_dialog import EmployeFormDialog

NOMS_ROLES = {
    "secretariat": "Secretariat",
    "comptabilite": "Comptabilite",
    "rh": "Ressources Humaines",
    "professeur": "Professeur",
    "super_admin": "Super Administrateur",
}


class EmployesRHWidget(QWidget):
    def __init__(self, role: str = None):
        super().__init__()
        self.role = role
        self._construire_interface()
        self._rafraichir()

    def _construire_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        entete = QHBoxLayout()
        titre = QLabel("Employes")
        titre.setStyleSheet("font-size: 20px; font-weight: bold;")
        entete.addWidget(titre)
        entete.addStretch()

        bouton_actualiser = QPushButton("Actualiser")
        bouton_actualiser.clicked.connect(self._rafraichir)
        entete.addWidget(bouton_actualiser)

        bouton_ajouter = QPushButton("+ Ajouter un employe")
        bouton_ajouter.setStyleSheet(
            "background-color: #2563eb; color: white; font-weight: bold; padding: 6px 12px;"
        )
        bouton_ajouter.clicked.connect(self._ouvrir_formulaire_ajout)
        entete.addWidget(bouton_ajouter)

        layout.addLayout(entete)

        self.tableau = QTableWidget()
        colonnes = ["Nom complet", "Identifiant", "Role", "Poste", "Departement", "Date d'embauche"]
        self.tableau.setColumnCount(len(colonnes))
        self.tableau.setHorizontalHeaderLabels(colonnes)
        self.tableau.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableau.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableau.setAlternatingRowColors(True)
        self.tableau.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableau.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        layout.addWidget(self.tableau)

        self.label_compteur = QLabel("")
        self.label_compteur.setStyleSheet("color: #666;")
        layout.addWidget(self.label_compteur)

    def _ouvrir_formulaire_ajout(self):
        dialogue = EmployeFormDialog(parent=self)
        if dialogue.exec() == EmployeFormDialog.Accepted:
            self._rafraichir()

    def _rafraichir(self):
        employes = employes_rh_repository.lister_employes()
        self.tableau.setRowCount(len(employes))
        for ligne, e in enumerate(employes):
            self.tableau.setItem(ligne, 0, QTableWidgetItem(e["nom_complet"]))
            self.tableau.setItem(ligne, 1, QTableWidgetItem(e["username"]))
            self.tableau.setItem(ligne, 2, QTableWidgetItem(NOMS_ROLES.get(e["role"], e["role"])))
            self.tableau.setItem(ligne, 3, QTableWidgetItem(e["poste"]))
            self.tableau.setItem(ligne, 4, QTableWidgetItem(e["departement"]))
            self.tableau.setItem(ligne, 5, QTableWidgetItem(e.get("date_embauche") or "-"))
        self.label_compteur.setText(f"{len(employes)} employe(s)")
