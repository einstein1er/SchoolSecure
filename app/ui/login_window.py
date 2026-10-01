"""
Ecran de connexion.
Regle de la couche UI : ce widget ne fait JAMAIS de SQL directement.
Il appelle uniquement app.repositories.users_repository, qui gere
le hachage/verification du mot de passe et le dechiffrement.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QLabel, QMessageBox
)
from PySide6.QtCore import Signal, Qt

from app.repositories import users_repository


class LoginWindow(QWidget):
    # Signal emis quand la connexion reussit, transporte l'utilisateur (dict)
    connexion_reussie = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion Scolaire - Connexion")
        self.setMinimumWidth(380)
        self._construire_interface()

    def _construire_interface(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setSpacing(16)
        layout_principal.setContentsMargins(32, 32, 32, 32)

        titre = QLabel("Connexion")
        titre.setStyleSheet("font-size: 20px; font-weight: bold;")
        titre.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(titre)

        formulaire = QFormLayout()
        formulaire.setSpacing(10)

        self.champ_username = QLineEdit()
        self.champ_username.setPlaceholderText("ex: secretaire_test")
        formulaire.addRow("Identifiant :", self.champ_username)

        self.champ_mot_de_passe = QLineEdit()
        self.champ_mot_de_passe.setEchoMode(QLineEdit.Password)
        self.champ_mot_de_passe.setPlaceholderText("Mot de passe")
        formulaire.addRow("Mot de passe :", self.champ_mot_de_passe)

        layout_principal.addLayout(formulaire)

        self.bouton_connexion = QPushButton("Se connecter")
        self.bouton_connexion.setMinimumHeight(36)
        self.bouton_connexion.clicked.connect(self._tenter_connexion)
        layout_principal.addWidget(self.bouton_connexion)

        self.label_erreur = QLabel("")
        self.label_erreur.setStyleSheet("color: #c0392b;")
        self.label_erreur.setAlignment(Qt.AlignCenter)
        self.label_erreur.setWordWrap(True)
        layout_principal.addWidget(self.label_erreur)

        # Permet de valider avec la touche Entree depuis le champ mot de passe
        self.champ_mot_de_passe.returnPressed.connect(self._tenter_connexion)

    def _tenter_connexion(self):
        username = self.champ_username.text().strip()
        mot_de_passe = self.champ_mot_de_passe.text()

        if not username or not mot_de_passe:
            self.label_erreur.setText("Veuillez remplir l'identifiant et le mot de passe.")
            return

        try:
            utilisateur = users_repository.verifier_identifiants(username, mot_de_passe)
        except Exception as e:
            # Aucune exception technique ne doit jamais faire planter l'appli
            QMessageBox.critical(self, "Erreur technique", f"Une erreur est survenue : {e}")
            return

        if utilisateur is None:
            self.label_erreur.setText("Identifiant ou mot de passe incorrect.")
            self.champ_mot_de_passe.clear()
            return

        self.label_erreur.setText("")
        self.connexion_reussie.emit(utilisateur)
