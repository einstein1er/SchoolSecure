"""
Ecran "Mes eleves" pour le role professeur.
Lecture seule, pedagogique uniquement : nom, prenom, classe.
Aucune information financiere -- ce n'est pas le role d'un professeur.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton
)

from app.business.prof_service import lister_eleves_du_professeur, lister_classes_du_professeur


class DashboardProfWidget(QWidget):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self._construire_interface()

    def _construire_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        entete = QHBoxLayout()
        titre = QLabel("Mes eleves")
        titre.setStyleSheet("font-size: 20px; font-weight: bold;")
        entete.addWidget(titre)
        entete.addStretch()
        bouton_actualiser = QPushButton("Actualiser")
        bouton_actualiser.clicked.connect(self._rafraichir)
        entete.addWidget(bouton_actualiser)
        layout.addLayout(entete)

        classes = lister_classes_du_professeur(self.user_id)
        noms_classes = ", ".join(c["nom"] for c in classes) if classes else "aucune classe assignee"
        sous_titre = QLabel(f"Classes : {noms_classes}")
        sous_titre.setStyleSheet("color: #555;")
        layout.addWidget(sous_titre)

        self.tableau = QTableWidget()
        colonnes = ["Matricule", "Nom", "Prenom", "Classe"]
        self.tableau.setColumnCount(len(colonnes))
        self.tableau.setHorizontalHeaderLabels(colonnes)
        self.tableau.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableau.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableau.setAlternatingRowColors(True)
        self.tableau.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tableau.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        layout.addWidget(self.tableau)

        self.label_compteur = QLabel("")
        self.label_compteur.setStyleSheet("color: #666;")
        layout.addWidget(self.label_compteur)

        note = QLabel(
            "Cette liste est en lecture seule. Les informations financieres "
            "ne sont pas accessibles depuis cet ecran."
        )
        note.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(note)

        self._rafraichir()

    def _rafraichir(self):
        eleves = lister_eleves_du_professeur(self.user_id)
        self.tableau.setRowCount(len(eleves))
        for ligne, e in enumerate(eleves):
            self.tableau.setItem(ligne, 0, QTableWidgetItem(e["matricule"]))
            self.tableau.setItem(ligne, 1, QTableWidgetItem(e["nom"]))
            self.tableau.setItem(ligne, 2, QTableWidgetItem(e["prenom"]))
            self.tableau.setItem(ligne, 3, QTableWidgetItem(e["classe_nom"]))
        self.label_compteur.setText(f"{len(eleves)} eleve(s)")
