"""
Point d'entree de l'application.
Lancement : python main.py (racine du projet, venv actif)
"""

import sys
from PySide6.QtWidgets import QApplication

from app.ui.login_window import LoginWindow
from app.ui.main_window import MainWindow


class ApplicationScolaire:
    """Petit chef d'orchestre : bascule entre l'ecran de connexion
    et la fenetre principale selon l'etat de connexion."""

    def __init__(self):
        self.login_window = LoginWindow()
        self.main_window = None

        self.login_window.connexion_reussie.connect(self._sur_connexion_reussie)

    def demarrer(self):
        self.login_window.show()

    def _sur_connexion_reussie(self, utilisateur: dict):
        self.login_window.close()
        self.main_window = MainWindow(utilisateur)
        self.main_window.deconnexion_demandee.connect(self._sur_deconnexion)
        self.main_window.show()

    def _sur_deconnexion(self):
        self.main_window.close()
        self.main_window = None
        self.login_window.champ_username.clear()
        self.login_window.champ_mot_de_passe.clear()
        self.login_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    application = ApplicationScolaire()
    application.demarrer()
    sys.exit(app.exec())
