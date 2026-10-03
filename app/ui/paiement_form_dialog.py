"""
Dialogue d'enregistrement d'un paiement pour un eleve donne.
Reutilise entierement la validation deja testee dans
paiements_repository.enregistrer_paiement() (impossible de depasser
le solde restant).
"""

from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout, QLineEdit, QComboBox,
    QPushButton, QLabel, QMessageBox
)

from app.business.eleve_service import fiche_complete_eleve
from app.repositories import paiements_repository
from app.business.soldes import MontantInvalideError

MODES_PAIEMENT = [
    ("Especes", "especes"),
    ("Cheque", "cheque"),
    ("Virement", "virement"),
    ("Mobile Money", "mobile_money"),
]


class PaiementFormDialog(QDialog):
    def __init__(self, eleve_id: int, enregistre_par: int, parent=None):
        super().__init__(parent)
        self.eleve_id = eleve_id
        self.enregistre_par = enregistre_par
        self.fiche = fiche_complete_eleve(eleve_id)
        self.paiement_enregistre = None  # rempli apres succes, utile pour l'appelant

        self.setWindowTitle("Enregistrer un paiement")
        self.setMinimumWidth(400)
        self._construire_interface()

    def _construire_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        titre = QLabel("Enregistrer un paiement")
        titre.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(titre)

        info_eleve = QLabel(f"{self.fiche['prenom']} {self.fiche['nom']}  ({self.fiche['matricule']})")
        info_eleve.setStyleSheet("color: #555;")
        layout.addWidget(info_eleve)

        info_solde = QLabel(f"Solde restant : {self.fiche['solde']:,.0f} FCFA".replace(",", " "))
        info_solde.setStyleSheet("font-size: 15px; font-weight: bold; color: #2563eb; margin-bottom: 8px;")
        layout.addWidget(info_solde)

        formulaire = QFormLayout()
        formulaire.setSpacing(10)

        self.champ_montant = QLineEdit()
        self.champ_montant.setPlaceholderText("ex: 50000")
        formulaire.addRow("Montant (FCFA) * :", self.champ_montant)

        self.champ_date = QLineEdit(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        formulaire.addRow("Date * :", self.champ_date)

        self.champ_mode = QComboBox()
        for libelle, valeur in MODES_PAIEMENT:
            self.champ_mode.addItem(libelle, userData=valeur)
        formulaire.addRow("Mode de paiement * :", self.champ_mode)

        layout.addLayout(formulaire)

        self.label_erreur = QLabel("")
        self.label_erreur.setStyleSheet("color: #c0392b;")
        self.label_erreur.setWordWrap(True)
        layout.addWidget(self.label_erreur)

        boutons = QHBoxLayout()
        bouton_annuler = QPushButton("Annuler")
        bouton_annuler.clicked.connect(self.reject)
        boutons.addWidget(bouton_annuler)

        bouton_enregistrer = QPushButton("Enregistrer le paiement")
        bouton_enregistrer.setDefault(True)
        bouton_enregistrer.setStyleSheet(
            "background-color: #16a34a; color: white; font-weight: bold; padding: 6px 12px;"
        )
        bouton_enregistrer.clicked.connect(self._enregistrer)
        boutons.addWidget(bouton_enregistrer)

        layout.addLayout(boutons)

    def _enregistrer(self):
        montant_texte = self.champ_montant.text().strip()
        date_paiement = self.champ_date.text().strip()
        mode_paiement = self.champ_mode.currentData()

        if not montant_texte:
            self.label_erreur.setText("Le montant est obligatoire.")
            return

        try:
            montant = float(montant_texte)
        except ValueError:
            self.label_erreur.setText("Le montant doit etre un nombre (ex: 50000).")
            return

        if not date_paiement:
            self.label_erreur.setText("La date est obligatoire.")
            return

        try:
            self.paiement_enregistre = paiements_repository.enregistrer_paiement(
                self.eleve_id, montant, mode_paiement, self.enregistre_par, date_paiement=date_paiement
            )
        except MontantInvalideError as e:
            # Exactement la regle du brief : le montant ne peut pas depasser le solde
            self.label_erreur.setText(str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Erreur technique", f"Une erreur est survenue : {e}")
            return

        self.accept()
