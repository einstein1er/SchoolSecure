"""
Dashboard eleve (lecture seule) : l'eleve connecte voit sa propre fiche
(infos, solde, statut, historique de paiements) mais ne peut RIEN
modifier. Pas de bouton paiement, pas de bouton modifier.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtGui import QColor

from app.repositories import eleves_repository, classes_repository
from app.business.eleve_service import fiche_complete_eleve

COULEURS_STATUT = {
    "Solde": QColor("#16a34a"),
    "Partiellement paye": QColor("#d97706"),
    "Non paye": QColor("#dc2626"),
}

LIBELLES_MODE_PAIEMENT = {
    "especes": "Especes",
    "cheque": "Cheque",
    "virement": "Virement",
    "mobile_money": "Mobile Money",
}


class DashboardEleveWidget(QWidget):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self._construire_interface()

    def _construire_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        eleve = eleves_repository.obtenir_eleve_par_user_id(self.user_id)

        if eleve is None:
            label = QLabel("Aucune fiche eleve n'est associee a ce compte. Contactez le secretariat.")
            label.setStyleSheet("color: #888; font-style: italic;")
            layout.addWidget(label)
            return

        fiche = fiche_complete_eleve(eleve["id"])
        classe = classes_repository.obtenir_classe(fiche["classe_id"])
        nom_classe = classe["nom"] if classe else "?"

        titre = QLabel(f"Bonjour, {fiche['prenom']} {fiche['nom']}")
        titre.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(titre)

        sous_titre = QLabel(f"Matricule : {fiche['matricule']}  |  Classe : {nom_classe}  |  Annee : {fiche['annee_scolaire']}")
        sous_titre.setStyleSheet("color: #555;")
        layout.addWidget(sous_titre)

        grille = QGridLayout()
        grille.setHorizontalSpacing(32)
        grille.addWidget(self._bloc_montant("Total du", fiche["total_du"]), 0, 0)
        grille.addWidget(self._bloc_montant("Total paye", fiche["total_paye"]), 0, 1)
        grille.addWidget(self._bloc_montant("Solde restant", fiche["solde"]), 0, 2)
        grille.addWidget(self._bloc_statut(fiche["statut"]), 0, 3)
        layout.addLayout(grille)

        titre_historique = QLabel("Mes paiements")
        titre_historique.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 12px;")
        layout.addWidget(titre_historique)

        tableau = QTableWidget()
        colonnes = ["Date", "Montant", "Mode", "N\u00b0 Recu", "Solde apres"]
        tableau.setColumnCount(len(colonnes))
        tableau.setHorizontalHeaderLabels(colonnes)
        tableau.setEditTriggers(QTableWidget.NoEditTriggers)
        tableau.setSelectionBehavior(QTableWidget.SelectRows)
        tableau.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

        paiements = fiche["paiements"]
        tableau.setRowCount(len(paiements))
        for ligne, p in enumerate(paiements):
            tableau.setItem(ligne, 0, QTableWidgetItem(p["date_paiement"]))
            tableau.setItem(ligne, 1, QTableWidgetItem(f"{p['montant']:,.0f}".replace(",", " ")))
            tableau.setItem(ligne, 2, QTableWidgetItem(LIBELLES_MODE_PAIEMENT.get(p["mode_paiement"], p["mode_paiement"])))
            tableau.setItem(ligne, 3, QTableWidgetItem(p["numero_recu"]))
            tableau.setItem(ligne, 4, QTableWidgetItem(f"{p['solde_apres']:,.0f}".replace(",", " ")))
        layout.addWidget(tableau)

        if not paiements:
            label_vide = QLabel("Aucun paiement enregistre pour le moment.")
            label_vide.setStyleSheet("color: #888; font-style: italic;")
            layout.addWidget(label_vide)

        note = QLabel("Cette page est en lecture seule. Pour toute question sur vos paiements, contactez le secretariat.")
        note.setStyleSheet("color: #888; font-size: 11px; margin-top: 8px;")
        layout.addWidget(note)

    def _bloc_montant(self, libelle_text: str, valeur: float) -> QWidget:
        bloc = QVBoxLayout()
        libelle = QLabel(libelle_text)
        libelle.setStyleSheet("color: #888; font-size: 12px;")
        valeur_label = QLabel(f"{valeur:,.0f} FCFA".replace(",", " "))
        valeur_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        bloc.addWidget(libelle)
        bloc.addWidget(valeur_label)
        conteneur = QWidget()
        conteneur.setLayout(bloc)
        return conteneur

    def _bloc_statut(self, statut: str) -> QWidget:
        bloc = QVBoxLayout()
        libelle = QLabel("Statut")
        libelle.setStyleSheet("color: #888; font-size: 12px;")
        couleur = COULEURS_STATUT.get(statut, QColor("#000")).name()
        valeur_label = QLabel(statut)
        valeur_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {couleur};")
        bloc.addWidget(libelle)
        bloc.addWidget(valeur_label)
        conteneur = QWidget()
        conteneur.setLayout(bloc)
        return conteneur
