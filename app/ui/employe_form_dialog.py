"""
Formulaire d'ajout d'un nouvel employe (hors eleve). Cree a la fois son
compte de connexion (users) et sa fiche RH (employes_rh). Repond a deux
besoins : module RH basique, et possibilite pour le directeur de creer
des comptes pour de nouveaux profs/membres de l'administration.
"""

import re

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout, QLineEdit, QComboBox,
    QPushButton, QLabel, QMessageBox
)

from app.repositories import users_repository, employes_rh_repository, professeurs_repository

ROLES_DISPONIBLES = [
    ("Secretariat", "secretariat"),
    ("Comptabilite", "comptabilite"),
    ("Ressources Humaines", "rh"),
    ("Professeur", "professeur"),
]


class EmployeFormDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un employe")
        self.setMinimumWidth(420)
        self._construire_interface()

    def _construire_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        titre = QLabel("Ajouter un employe")
        titre.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(titre)

        formulaire = QFormLayout()
        formulaire.setSpacing(10)

        self.champ_nom_complet = QLineEdit()
        self.champ_nom_complet.setPlaceholderText("ex: Ama KOSSI")
        formulaire.addRow("Nom complet * :", self.champ_nom_complet)

        self.champ_username = QLineEdit()
        self.champ_username.setPlaceholderText("ex: ama.kossi")
        formulaire.addRow("Identifiant de connexion * :", self.champ_username)

        self.champ_mot_de_passe = QLineEdit()
        self.champ_mot_de_passe.setEchoMode(QLineEdit.Password)
        self.champ_mot_de_passe.setPlaceholderText("Mot de passe temporaire")
        formulaire.addRow("Mot de passe * :", self.champ_mot_de_passe)

        self.champ_role = QComboBox()
        for libelle, valeur in ROLES_DISPONIBLES:
            self.champ_role.addItem(libelle, userData=valeur)
        formulaire.addRow("Role (compte) * :", self.champ_role)

        self.champ_poste = QLineEdit()
        self.champ_poste.setPlaceholderText("ex: Secretaire administrative")
        formulaire.addRow("Poste * :", self.champ_poste)

        self.champ_departement = QLineEdit()
        self.champ_departement.setPlaceholderText("ex: Administration")
        formulaire.addRow("Departement * :", self.champ_departement)

        self.champ_date_embauche = QLineEdit()
        self.champ_date_embauche.setPlaceholderText("AAAA-MM-JJ (optionnel)")
        formulaire.addRow("Date d'embauche :", self.champ_date_embauche)

        layout.addLayout(formulaire)

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

    def _enregistrer(self):
        nom_complet = self.champ_nom_complet.text().strip()
        username = self.champ_username.text().strip()
        mot_de_passe = self.champ_mot_de_passe.text()
        role = self.champ_role.currentData()
        poste = self.champ_poste.text().strip()
        departement = self.champ_departement.text().strip()
        date_embauche = self.champ_date_embauche.text().strip() or None

        if not nom_complet or not username or not mot_de_passe or not poste or not departement:
            self.label_erreur.setText("Tous les champs marques * sont obligatoires.")
            return

        if len(mot_de_passe) < 6:
            self.label_erreur.setText("Le mot de passe doit contenir au moins 6 caracteres.")
            return

        if date_embauche and not re.match(r"^\d{4}-\d{2}-\d{2}$", date_embauche):
            self.label_erreur.setText("La date d'embauche doit etre au format AAAA-MM-JJ.")
            return

        try:
            user_id = users_repository.creer_utilisateur(username, mot_de_passe, role, nom_complet)
        except Exception as e:
            # Cas frequent : identifiant deja pris (contrainte UNIQUE en base)
            self.label_erreur.setText(f"Impossible de creer le compte (identifiant deja utilise ?) : {e}")
            return

        try:
            employes_rh_repository.ajouter_employe(user_id, poste, departement, date_embauche)
            if role == "professeur":
                professeurs_repository.creer_professeur(user_id)
        except Exception as e:
            QMessageBox.critical(self, "Erreur technique", f"Compte cree, mais erreur sur la fiche RH : {e}")
            return

        self.accept()
