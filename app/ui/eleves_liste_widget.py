"""
Ecran "Liste des eleves".
Regle de la couche UI : ce widget ne fait JAMAIS de SQL directement,
il appelle uniquement la couche business/repository deja testee.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QLabel, QPushButton, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.business.eleve_service import liste_eleves_avec_statut
from app.repositories import classes_repository

COULEURS_STATUT = {
    "Solde": QColor("#16a34a"),              # vert
    "Partiellement paye": QColor("#d97706"),  # orange
    "Non paye": QColor("#dc2626"),            # rouge
}

COLONNES = ["Nom", "Prenom", "Classe", "Total du", "Total paye", "Solde", "Statut"]


class _ItemMontant(QTableWidgetItem):
    """Cellule qui s'affiche formatee ('125 000') mais se trie TOUJOURS
    numeriquement, en comparant la valeur brute plutot que le texte
    affiche (sinon '9000' se classerait avant '150000', par exemple)."""

    def __init__(self, valeur: float):
        super().__init__(f"{valeur:,.0f}".replace(",", " "))
        self.valeur = valeur

    def __lt__(self, autre):
        if isinstance(autre, _ItemMontant):
            return self.valeur < autre.valeur
        return super().__lt__(autre)


def _item_montant(valeur: float) -> QTableWidgetItem:
    return _ItemMontant(valeur)


class ElevesListeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.classes = []  # liste des classes chargees (pour mapper nom <-> id)
        self._construire_interface()
        self._charger_classes()
        self._rafraichir_tableau()
        self._rafraichir_recap()

    def _construire_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        titre = QLabel("Liste des eleves")
        titre.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(titre)

        # --- Barre de recherche + filtre ---
        barre_outils = QHBoxLayout()

        self.champ_recherche = QLineEdit()
        self.champ_recherche.setPlaceholderText("Rechercher un eleve (nom ou prenom)...")
        self.champ_recherche.textChanged.connect(self._rafraichir_tableau)
        barre_outils.addWidget(self.champ_recherche, stretch=2)

        self.filtre_classe = QComboBox()
        self.filtre_classe.currentIndexChanged.connect(self._rafraichir_tableau)
        barre_outils.addWidget(self.filtre_classe, stretch=1)

        bouton_actualiser = QPushButton("Actualiser")
        bouton_actualiser.clicked.connect(self._rafraichir_complet)
        barre_outils.addWidget(bouton_actualiser)

        layout.addLayout(barre_outils)

        # --- Tableau ---
        self.tableau = QTableWidget()
        self.tableau.setColumnCount(len(COLONNES))
        self.tableau.setHorizontalHeaderLabels(COLONNES)
        self.tableau.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableau.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableau.setAlternatingRowColors(True)
        self.tableau.setSortingEnabled(True)  # clic sur un en-tete = tri sur cette colonne
        self.tableau.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableau.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.tableau)

        self.label_compteur = QLabel("")
        self.label_compteur.setStyleSheet("color: #666;")
        layout.addWidget(self.label_compteur)

        # --- Recapitulatif par classe ---
        titre_recap = QLabel("Recapitulatif par classe")
        titre_recap.setStyleSheet("font-size: 15px; font-weight: bold; margin-top: 8px;")
        layout.addWidget(titre_recap)

        self.tableau_recap = QTableWidget()
        self.tableau_recap.setColumnCount(5)
        self.tableau_recap.setHorizontalHeaderLabels(
            ["Classe", "Solde", "Partiellement paye", "Non paye", "Total eleves"]
        )
        self.tableau_recap.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableau_recap.setSelectionMode(QTableWidget.NoSelection)
        self.tableau_recap.setMaximumHeight(160)
        self.tableau_recap.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.tableau_recap)

    def _charger_classes(self):
        self.classes = classes_repository.lister_classes()
        self.filtre_classe.blockSignals(True)
        self.filtre_classe.clear()
        self.filtre_classe.addItem("Toutes les classes", userData=None)
        for c in self.classes:
            self.filtre_classe.addItem(c["nom"], userData=c["id"])
        self.filtre_classe.blockSignals(False)

    def _rafraichir_complet(self):
        self._charger_classes()
        self._rafraichir_tableau()
        self._rafraichir_recap()

    def _rafraichir_tableau(self):
        recherche = self.champ_recherche.text().strip() or None
        classe_id = self.filtre_classe.currentData()

        eleves = liste_eleves_avec_statut(classe_id=classe_id, recherche=recherche)
        noms_classes = {c["id"]: c["nom"] for c in self.classes}

        # On coupe le tri pendant le remplissage : sinon Qt re-trie a
        # chaque ligne ajoutee et les indices de ligne deviennent faux.
        self.tableau.setSortingEnabled(False)
        self.tableau.setRowCount(len(eleves))
        for ligne, eleve in enumerate(eleves):
            self.tableau.setItem(ligne, 0, QTableWidgetItem(eleve["nom"]))
            self.tableau.setItem(ligne, 1, QTableWidgetItem(eleve["prenom"]))
            self.tableau.setItem(ligne, 2, QTableWidgetItem(noms_classes.get(eleve["classe_id"], "?")))
            self.tableau.setItem(ligne, 3, _item_montant(eleve["total_du"]))
            self.tableau.setItem(ligne, 4, _item_montant(eleve["total_paye"]))
            self.tableau.setItem(ligne, 5, _item_montant(eleve["solde"]))

            item_statut = QTableWidgetItem(eleve["statut"])
            couleur = COULEURS_STATUT.get(eleve["statut"])
            if couleur:
                item_statut.setForeground(couleur)
            item_statut.setTextAlignment(Qt.AlignCenter)
            self.tableau.setItem(ligne, 6, item_statut)

            # On garde l'id eleve accessible sur la ligne pour les futurs ecrans
            # (fiche detaillee / paiement) qui viendront se brancher dessus.
            self.tableau.item(ligne, 0).setData(Qt.UserRole, eleve["id"])

        self.tableau.setSortingEnabled(True)
        self.label_compteur.setText(f"{len(eleves)} eleve(s) affiche(s)")

    def _rafraichir_recap(self):
        """Tableau recapitulatif : nombre d'eleves par classe et par statut.
        Toujours base sur TOUS les eleves (independant de la recherche/filtre
        du tableau principal), car c'est une vue d'ensemble de l'etablissement."""
        tous_les_eleves = liste_eleves_avec_statut()
        noms_classes = {c["id"]: c["nom"] for c in self.classes}

        # Regroupement : {classe_id: {"Solde": x, "Partiellement paye": y, "Non paye": z}}
        compteurs = {}
        for eleve in tous_les_eleves:
            cid = eleve["classe_id"]
            compteurs.setdefault(cid, {"Solde": 0, "Partiellement paye": 0, "Non paye": 0})
            compteurs[cid][eleve["statut"]] += 1

        classes_triees = sorted(compteurs.keys(), key=lambda cid: noms_classes.get(cid, ""))

        self.tableau_recap.setRowCount(len(classes_triees))
        for ligne, cid in enumerate(classes_triees):
            stats = compteurs[cid]
            total = stats["Solde"] + stats["Partiellement paye"] + stats["Non paye"]

            self.tableau_recap.setItem(ligne, 0, QTableWidgetItem(noms_classes.get(cid, "?")))

            item_solde = QTableWidgetItem(str(stats["Solde"]))
            item_solde.setForeground(COULEURS_STATUT["Solde"])
            item_solde.setTextAlignment(Qt.AlignCenter)
            self.tableau_recap.setItem(ligne, 1, item_solde)

            item_partiel = QTableWidgetItem(str(stats["Partiellement paye"]))
            item_partiel.setForeground(COULEURS_STATUT["Partiellement paye"])
            item_partiel.setTextAlignment(Qt.AlignCenter)
            self.tableau_recap.setItem(ligne, 2, item_partiel)

            item_non_paye = QTableWidgetItem(str(stats["Non paye"]))
            item_non_paye.setForeground(COULEURS_STATUT["Non paye"])
            item_non_paye.setTextAlignment(Qt.AlignCenter)
            self.tableau_recap.setItem(ligne, 3, item_non_paye)

            item_total = QTableWidgetItem(str(total))
            item_total.setTextAlignment(Qt.AlignCenter)
            font = item_total.font()
            font.setBold(True)
            item_total.setFont(font)
            self.tableau_recap.setItem(ligne, 4, item_total)
