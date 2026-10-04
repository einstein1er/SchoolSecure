"""
Tableau de bord : vue d'ensemble de l'etablissement.
D'apres le brief : nombre d'eleves, total encaisse, total restant du,
nombre d'eleves non soldes, et une liste triee par statut de paiement.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.business.eleve_service import liste_eleves_avec_statut
from app.repositories import classes_repository

COULEURS_STATUT = {
    "Solde": QColor("#16a34a"),
    "Partiellement paye": QColor("#d97706"),
    "Non paye": QColor("#dc2626"),
}


class TableauBordWidget(QWidget):
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
        titre = QLabel("Tableau de bord")
        titre.setStyleSheet("font-size: 20px; font-weight: bold;")
        entete.addWidget(titre)
        entete.addStretch()
        bouton_actualiser = QPushButton("Actualiser")
        bouton_actualiser.clicked.connect(self._rafraichir)
        entete.addWidget(bouton_actualiser)
        layout.addLayout(entete)

        # --- Cartes de statistiques ---
        self.grille_cartes = QGridLayout()
        self.grille_cartes.setSpacing(16)
        layout.addLayout(self.grille_cartes)

        self.carte_nb_eleves = self._creer_carte("Nombre d'eleves", "#2563eb")
        self.carte_total_encaisse = self._creer_carte("Total encaisse", "#16a34a")
        self.carte_total_restant = self._creer_carte("Total restant du", "#d97706")
        self.carte_non_soldes = self._creer_carte("Eleves non soldes", "#dc2626")

        self.grille_cartes.addWidget(self.carte_nb_eleves["conteneur"], 0, 0)
        self.grille_cartes.addWidget(self.carte_total_encaisse["conteneur"], 0, 1)
        self.grille_cartes.addWidget(self.carte_total_restant["conteneur"], 0, 2)
        self.grille_cartes.addWidget(self.carte_non_soldes["conteneur"], 0, 3)

        # --- Liste des eleves non soldes, triee par urgence (solde decroissant) ---
        titre_liste = QLabel("Eleves a relancer en priorite (solde restant le plus eleve)")
        titre_liste.setStyleSheet("font-size: 15px; font-weight: bold; margin-top: 8px;")
        layout.addWidget(titre_liste)

        self.tableau = QTableWidget()
        colonnes = ["Nom", "Prenom", "Classe", "Solde restant", "Statut"]
        self.tableau.setColumnCount(len(colonnes))
        self.tableau.setHorizontalHeaderLabels(colonnes)
        self.tableau.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableau.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableau.setAlternatingRowColors(True)
        self.tableau.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableau.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.tableau)

        note = QLabel("Pour la liste complete avec recherche et modification, utilisez le menu \u00ab Eleves \u00bb.")
        note.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(note)

    def _creer_carte(self, libelle: str, couleur: str) -> dict:
        conteneur = QFrame()
        conteneur.setStyleSheet(
            f"QFrame {{ background-color: #f8fafc; border-left: 4px solid {couleur}; "
            f"border-radius: 4px; padding: 4px; }}"
        )
        layout_carte = QVBoxLayout(conteneur)
        layout_carte.setContentsMargins(16, 12, 16, 12)

        label_libelle = QLabel(libelle)
        label_libelle.setStyleSheet("color: #666; font-size: 12px;")
        layout_carte.addWidget(label_libelle)

        label_valeur = QLabel("...")
        label_valeur.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {couleur};")
        layout_carte.addWidget(label_valeur)

        return {"conteneur": conteneur, "valeur": label_valeur}

    def _rafraichir(self):
        eleves = liste_eleves_avec_statut()
        noms_classes = {c["id"]: c["nom"] for c in classes_repository.lister_classes()}

        nb_eleves = len(eleves)
        total_encaisse = sum(e["total_paye"] for e in eleves)
        total_restant = sum(e["solde"] for e in eleves)
        nb_non_soldes = sum(1 for e in eleves if e["statut"] != "Solde")

        self.carte_nb_eleves["valeur"].setText(str(nb_eleves))
        self.carte_total_encaisse["valeur"].setText(f"{total_encaisse:,.0f}".replace(",", " "))
        self.carte_total_restant["valeur"].setText(f"{total_restant:,.0f}".replace(",", " "))
        self.carte_non_soldes["valeur"].setText(str(nb_non_soldes))

        eleves_non_soldes = sorted(
            (e for e in eleves if e["statut"] != "Solde"),
            key=lambda e: e["solde"], reverse=True
        )

        self.tableau.setRowCount(len(eleves_non_soldes))
        for ligne, e in enumerate(eleves_non_soldes):
            self.tableau.setItem(ligne, 0, QTableWidgetItem(e["nom"]))
            self.tableau.setItem(ligne, 1, QTableWidgetItem(e["prenom"]))
            self.tableau.setItem(ligne, 2, QTableWidgetItem(noms_classes.get(e["classe_id"], "?")))
            self.tableau.setItem(ligne, 3, QTableWidgetItem(f"{e['solde']:,.0f}".replace(",", " ")))

            item_statut = QTableWidgetItem(e["statut"])
            couleur = COULEURS_STATUT.get(e["statut"])
            if couleur:
                item_statut.setForeground(couleur)
            item_statut.setTextAlignment(Qt.AlignCenter)
            self.tableau.setItem(ligne, 4, item_statut)

        if not eleves_non_soldes:
            self.tableau.setRowCount(1)
            item_vide = QTableWidgetItem("Tous les eleves sont a jour \U0001F389")
            self.tableau.setItem(0, 0, item_vide)
            self.tableau.setSpan(0, 0, 1, 5)
