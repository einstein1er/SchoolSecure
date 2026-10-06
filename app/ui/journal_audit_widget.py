"""
Journal d'audit : trace qui a fait quoi, et quand. Lecture seule,
reserve au super_admin.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton
)

from app.repositories import audit_log_repository

NOMS_ROLES = {
    "super_admin": "Directeur",
    "secretariat": "Secretariat",
    "comptabilite": "Comptabilite",
    "rh": "RH",
    "professeur": "Professeur",
    "eleve": "Eleve",
    "parent": "Parent",
}


class JournalAuditWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._construire_interface()
        self._rafraichir()

    def _construire_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        entete = QHBoxLayout()
        titre = QLabel("Journal d'audit")
        titre.setStyleSheet("font-size: 20px; font-weight: bold;")
        entete.addWidget(titre)
        entete.addStretch()
        bouton_actualiser = QPushButton("Actualiser")
        bouton_actualiser.clicked.connect(self._rafraichir)
        entete.addWidget(bouton_actualiser)
        layout.addLayout(entete)

        note = QLabel("Affiche les 300 dernieres actions enregistrees dans l'application.")
        note.setStyleSheet("color: #666;")
        layout.addWidget(note)

        self.tableau = QTableWidget()
        colonnes = ["Date", "Utilisateur", "Role", "Action", "Table", "Details"]
        self.tableau.setColumnCount(len(colonnes))
        self.tableau.setHorizontalHeaderLabels(colonnes)
        self.tableau.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableau.setAlternatingRowColors(True)
        self.tableau.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        layout.addWidget(self.tableau)

        self.label_compteur = QLabel("")
        self.label_compteur.setStyleSheet("color: #666;")
        layout.addWidget(self.label_compteur)

    def _rafraichir(self):
        entrees = audit_log_repository.lister(limite=300)
        self.tableau.setRowCount(len(entrees))
        for ligne, e in enumerate(entrees):
            self.tableau.setItem(ligne, 0, QTableWidgetItem((e.get("date_action") or "")[:19]))
            self.tableau.setItem(ligne, 1, QTableWidgetItem(e.get("nom_utilisateur") or "?"))
            self.tableau.setItem(ligne, 2, QTableWidgetItem(NOMS_ROLES.get(e.get("role"), e.get("role") or "?")))
            self.tableau.setItem(ligne, 3, QTableWidgetItem(e.get("action") or ""))
            self.tableau.setItem(ligne, 4, QTableWidgetItem(e.get("table_concernee") or ""))
            self.tableau.setItem(ligne, 5, QTableWidgetItem(e.get("details") or ""))
        self.label_compteur.setText(f"{len(entrees)} entree(s)")
