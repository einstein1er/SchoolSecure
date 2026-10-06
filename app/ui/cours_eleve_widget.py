"""
Ecran "Mes cours" pour l'eleve : liste en lecture seule des cours
deposes par ses professeurs pour SA classe, avec possibilite de
telecharger le PDF s'il y en a un.
"""

import shutil

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QFileDialog, QMessageBox
)

from app.repositories import eleves_repository, cours_repository, professeurs_repository, users_repository
from app.business.stockage_fichiers import obtenir_chemin_absolu


class CoursEleveWidget(QWidget):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self._construire_interface()

    def _construire_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        titre = QLabel("Mes cours")
        titre.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(titre)

        eleve = eleves_repository.obtenir_eleve_par_user_id(self.user_id)
        if eleve is None:
            label = QLabel("Aucune fiche eleve n'est associee a ce compte. Contactez le secretariat.")
            label.setStyleSheet("color: #888; font-style: italic;")
            layout.addWidget(label)
            return

        cours = cours_repository.lister_cours_par_classe(eleve["classe_id"])

        self.tableau = QTableWidget()
        colonnes = ["Titre", "Professeur", "Description", "Date", "Telechargement"]
        self.tableau.setColumnCount(len(colonnes))
        self.tableau.setHorizontalHeaderLabels(colonnes)
        self.tableau.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableau.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableau.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tableau.setRowCount(len(cours))

        for ligne, c in enumerate(cours):
            nom_prof = self._nom_professeur(c["professeur_id"])
            self.tableau.setItem(ligne, 0, QTableWidgetItem(c["titre"]))
            self.tableau.setItem(ligne, 1, QTableWidgetItem(nom_prof))
            self.tableau.setItem(ligne, 2, QTableWidgetItem(c.get("description") or ""))
            self.tableau.setItem(ligne, 3, QTableWidgetItem((c.get("date_creation") or "")[:10]))

            if c.get("fichier_pdf"):
                bouton = QPushButton("Telecharger")
                bouton.clicked.connect(lambda checked, nom_fichier=c["fichier_pdf"], titre_cours=c["titre"]: self._telecharger(nom_fichier, titre_cours))
                self.tableau.setCellWidget(ligne, 4, bouton)
            else:
                self.tableau.setItem(ligne, 4, QTableWidgetItem("Pas de fichier"))

        layout.addWidget(self.tableau)

        if not cours:
            label_vide = QLabel("Aucun cours n'a encore ete depose pour votre classe.")
            label_vide.setStyleSheet("color: #888; font-style: italic;")
            layout.addWidget(label_vide)

    def _nom_professeur(self, professeur_id: int) -> str:
        """Retrouve le nom affichable du professeur a partir de son id technique."""
        from app.database.db_connection import get_connection
        connexion = get_connection()
        try:
            ligne = connexion.execute(
                "SELECT user_id FROM professeurs WHERE id = ?", (professeur_id,)
            ).fetchone()
        finally:
            connexion.close()
        if ligne is None:
            return "?"
        utilisateur = users_repository.obtenir_utilisateur(ligne["user_id"])
        return utilisateur["nom_complet"] if utilisateur else "?"

    def _telecharger(self, nom_fichier: str, titre_cours: str):
        chemin_source = obtenir_chemin_absolu(nom_fichier)
        if not chemin_source.exists():
            QMessageBox.warning(self, "Introuvable", "Ce fichier n'est plus disponible.")
            return

        nom_suggere = f"{titre_cours}.pdf"
        chemin_destination, _ = QFileDialog.getSaveFileName(self, "Enregistrer le cours", nom_suggere, "Fichiers PDF (*.pdf)")
        if not chemin_destination:
            return

        try:
            shutil.copy2(chemin_source, chemin_destination)
            QMessageBox.information(self, "Telecharge", f"Le cours a ete enregistre :\n{chemin_destination}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur technique", f"Impossible de copier le fichier : {e}")
