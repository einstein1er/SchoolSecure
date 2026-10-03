"""
Fiche detaillee d'un eleve : infos + solde + statut + historique complet
des paiements, avec possibilite de revoir un recu deja emis.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.business.eleve_service import fiche_complete_eleve
from app.repositories import classes_repository

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

ROLES_EDITION_AUTORISES = {"super_admin", "secretariat"}


class EleveFicheDialog(QDialog):
    def __init__(self, role: str, eleve_id: int, parent=None):
        super().__init__(parent)
        self.role = role
        self.eleve_id = eleve_id
        self.peut_editer = role in ROLES_EDITION_AUTORISES
        self.fiche = fiche_complete_eleve(eleve_id)

        self.setWindowTitle("Fiche eleve")
        self.setMinimumSize(700, 550)
        self._construire_interface()

    def _construire_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        if self.fiche is None:
            layout.addWidget(QLabel("Eleve introuvable."))
            return

        f = self.fiche
        classe = classes_repository.obtenir_classe(f["classe_id"])
        nom_classe = classe["nom"] if classe else "?"

        # --- En-tete infos generales ---
        titre = QLabel(f"{f['prenom']} {f['nom']}")
        titre.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(titre)

        sous_titre = QLabel(f"Matricule : {f['matricule']}  |  Classe : {nom_classe}  |  Annee : {f['annee_scolaire']}")
        sous_titre.setStyleSheet("color: #555;")
        layout.addWidget(sous_titre)

        grille_montants = QGridLayout()
        grille_montants.setHorizontalSpacing(32)

        grille_montants.addWidget(self._bloc_montant("Total du", f["total_du"]), 0, 0)
        grille_montants.addWidget(self._bloc_montant("Total paye", f["total_paye"]), 0, 1)
        grille_montants.addWidget(self._bloc_montant("Solde restant", f["solde"]), 0, 2)

        label_statut = QLabel(f["statut"])
        label_statut.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {COULEURS_STATUT.get(f['statut'], QColor('#000')).name()};"
        )
        bloc_statut = QVBoxLayout()
        libelle = QLabel("Statut")
        libelle.setStyleSheet("color: #888; font-size: 12px;")
        bloc_statut.addWidget(libelle)
        bloc_statut.addWidget(label_statut)
        conteneur_statut = self._enveloppe(bloc_statut)
        grille_montants.addWidget(conteneur_statut, 0, 3)

        layout.addLayout(grille_montants)

        # --- Historique des paiements ---
        titre_historique = QLabel("Historique des paiements")
        titre_historique.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 8px;")
        layout.addWidget(titre_historique)

        self.tableau_paiements = QTableWidget()
        colonnes = ["Date", "Montant", "Mode", "N\u00b0 Recu", "Solde apres", "Action"]
        self.tableau_paiements.setColumnCount(len(colonnes))
        self.tableau_paiements.setHorizontalHeaderLabels(colonnes)
        self.tableau_paiements.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableau_paiements.setSelectionBehavior(QTableWidget.SelectRows)
        self.tableau_paiements.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self._remplir_tableau_paiements()
        layout.addWidget(self.tableau_paiements)

        if not f["paiements"]:
            label_vide = QLabel("Aucun paiement enregistre pour cet eleve pour le moment.")
            label_vide.setStyleSheet("color: #888; font-style: italic;")
            layout.addWidget(label_vide)

        # --- Actions du bas ---
        boutons = QHBoxLayout()

        bouton_paiement = QPushButton("+ Enregistrer un paiement")
        bouton_paiement.setStyleSheet(
            "background-color: #16a34a; color: white; font-weight: bold; padding: 8px 14px;"
        )
        bouton_paiement.clicked.connect(self._enregistrer_paiement)
        boutons.addWidget(bouton_paiement)

        if self.peut_editer:
            bouton_modifier = QPushButton("Modifier les infos")
            bouton_modifier.clicked.connect(self._modifier_eleve)
            boutons.addWidget(bouton_modifier)

        boutons.addStretch()

        bouton_fermer = QPushButton("Fermer")
        bouton_fermer.clicked.connect(self.accept)
        boutons.addWidget(bouton_fermer)

        layout.addLayout(boutons)

    def _bloc_montant(self, libelle_text: str, valeur: float) -> "QWidget":
        bloc = QVBoxLayout()
        libelle = QLabel(libelle_text)
        libelle.setStyleSheet("color: #888; font-size: 12px;")
        valeur_label = QLabel(f"{valeur:,.0f} FCFA".replace(",", " "))
        valeur_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        bloc.addWidget(libelle)
        bloc.addWidget(valeur_label)
        return self._enveloppe(bloc)

    def _enveloppe(self, inner_layout) -> "QWidget":
        from PySide6.QtWidgets import QWidget
        w = QWidget()
        w.setLayout(inner_layout)
        return w

    def _remplir_tableau_paiements(self):
        paiements = self.fiche["paiements"]
        self.tableau_paiements.setRowCount(len(paiements))
        for ligne, p in enumerate(paiements):
            self.tableau_paiements.setItem(ligne, 0, QTableWidgetItem(p["date_paiement"]))
            self.tableau_paiements.setItem(ligne, 1, QTableWidgetItem(f"{p['montant']:,.0f}".replace(",", " ")))
            self.tableau_paiements.setItem(ligne, 2, QTableWidgetItem(LIBELLES_MODE_PAIEMENT.get(p["mode_paiement"], p["mode_paiement"])))
            self.tableau_paiements.setItem(ligne, 3, QTableWidgetItem(p["numero_recu"]))
            self.tableau_paiements.setItem(ligne, 4, QTableWidgetItem(f"{p['solde_apres']:,.0f}".replace(",", " ")))

            bouton_revoir = QPushButton("Revoir le recu")
            bouton_revoir.clicked.connect(lambda checked, num=p["numero_recu"]: self._revoir_recu(num))
            self.tableau_paiements.setCellWidget(ligne, 5, bouton_revoir)

    def _revoir_recu(self, numero_recu: str):
        """Version provisoire : affiche les details du recu dans une boite
        de dialogue. Sera remplace par un vrai recu PDF a l'etape suivante."""
        from app.repositories import paiements_repository
        p = paiements_repository.obtenir_paiement_par_numero(numero_recu)
        if p is None:
            QMessageBox.warning(self, "Introuvable", "Ce recu n'a pas ete trouve.")
            return
        message = (
            f"Recu N\u00b0 {p['numero_recu']}\n\n"
            f"Eleve : {self.fiche['prenom']} {self.fiche['nom']}\n"
            f"Date : {p['date_paiement']}\n"
            f"Montant : {p['montant']:,.0f} FCFA\n"
            f"Mode de paiement : {LIBELLES_MODE_PAIEMENT.get(p['mode_paiement'], p['mode_paiement'])}\n"
            f"Solde apres ce paiement : {p['solde_apres']:,.0f} FCFA\n\n"
            f"Hash de verification : {p['qr_hash'][:24]}..."
        ).replace(",", " ")
        QMessageBox.information(self, f"Recu {numero_recu}", message)

    def _enregistrer_paiement(self):
        QMessageBox.information(
            self, "A venir",
            "L'enregistrement de paiement sera disponible a la prochaine etape."
        )

    def _modifier_eleve(self):
        """Ouvre le formulaire de modification. Pour garder l'affichage de
        la fiche toujours coherent et simple (plutot que de reconstruire
        dynamiquement tous les widgets), on ferme la fiche apres une
        modification reussie -- l'utilisateur peut la rouvrir pour voir
        les infos a jour, via le bouton 'Voir' depuis la liste."""
        from app.ui.eleve_form_dialog import EleveFormDialog
        dialogue = EleveFormDialog(role=self.role, eleve_id=self.eleve_id, parent=self)
        if dialogue.exec() == EleveFormDialog.Accepted:
            self.accept()
