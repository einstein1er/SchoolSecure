"""
Formulaire d'ajout d'un cours par un professeur : titre, description,
classe (parmi celles assignees au prof), et upload d'un fichier PDF.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout, QLineEdit, QComboBox,
    QPushButton, QLabel, QTextEdit, QFileDialog, QMessageBox
)

from app.repositories import cours_repository, professeurs_repository
from app.business.stockage_fichiers import copier_fichier_cours


class CoursFormDialog(QDialog):
    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.professeur = professeurs_repository.obtenir_professeur_par_user_id(user_id)
        self.chemin_pdf_choisi = None

        self.setWindowTitle("Ajouter un cours")
        self.setMinimumWidth(440)
        self._construire_interface()

    def _construire_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        titre = QLabel("Ajouter un cours")
        titre.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(titre)

        formulaire = QFormLayout()
        formulaire.setSpacing(10)

        self.champ_classe = QComboBox()
        classes = professeurs_repository.lister_classes_du_professeur(self.professeur["id"]) if self.professeur else []
        for c in classes:
            self.champ_classe.addItem(c["nom"], userData=c["id"])
        formulaire.addRow("Classe * :", self.champ_classe)

        self.champ_titre = QLineEdit()
        self.champ_titre.setPlaceholderText("ex: Chapitre 3 - Les fractions")
        formulaire.addRow("Titre * :", self.champ_titre)

        self.champ_description = QTextEdit()
        self.champ_description.setMaximumHeight(80)
        formulaire.addRow("Description :", self.champ_description)

        layout.addLayout(formulaire)

        ligne_fichier = QHBoxLayout()
        self.label_fichier = QLabel("Aucun fichier choisi")
        self.label_fichier.setStyleSheet("color: #666;")
        ligne_fichier.addWidget(self.label_fichier, stretch=1)
        bouton_choisir = QPushButton("Choisir un PDF...")
        bouton_choisir.clicked.connect(self._choisir_fichier)
        ligne_fichier.addWidget(bouton_choisir)
        layout.addLayout(ligne_fichier)

        self.label_erreur = QLabel("")
        self.label_erreur.setStyleSheet("color: #c0392b;")
        self.label_erreur.setWordWrap(True)
        layout.addWidget(self.label_erreur)

        boutons = QHBoxLayout()
        bouton_annuler = QPushButton("Annuler")
        bouton_annuler.clicked.connect(self.reject)
        boutons.addWidget(bouton_annuler)

        bouton_ajouter = QPushButton("Ajouter")
        bouton_ajouter.setDefault(True)
        bouton_ajouter.clicked.connect(self._enregistrer)
        boutons.addWidget(bouton_ajouter)

        layout.addLayout(boutons)

    def _choisir_fichier(self):
        chemin, _ = QFileDialog.getOpenFileName(self, "Choisir le PDF du cours", "", "Fichiers PDF (*.pdf)")
        if chemin:
            self.chemin_pdf_choisi = chemin
            from pathlib import Path
            self.label_fichier.setText(Path(chemin).name)
            self.label_fichier.setStyleSheet("color: #16a34a;")

    def _enregistrer(self):
        if self.professeur is None:
            self.label_erreur.setText("Aucun profil professeur associe a ce compte.")
            return

        titre = self.champ_titre.text().strip()
        description = self.champ_description.toPlainText().strip()
        classe_id = self.champ_classe.currentData()

        if not titre:
            self.label_erreur.setText("Le titre est obligatoire.")
            return
        if classe_id is None:
            self.label_erreur.setText("Aucune classe assignee a votre compte. Contactez l'administration.")
            return

        fichier_pdf = None
        if self.chemin_pdf_choisi:
            try:
                fichier_pdf = copier_fichier_cours(self.chemin_pdf_choisi)
            except Exception as e:
                QMessageBox.critical(self, "Erreur technique", f"Impossible de copier le fichier PDF : {e}")
                return

        try:
            cours_repository.ajouter_cours(self.professeur["id"], classe_id, titre, description, fichier_pdf)
        except Exception as e:
            QMessageBox.critical(self, "Erreur technique", f"Une erreur est survenue : {e}")
            return

        self.accept()
