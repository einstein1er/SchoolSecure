"""
Ecran "Mes cours" pour le professeur : liste des cours qu'il a deposes
(avec upload PDF), et gestion simple de son emploi du temps.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QComboBox, QLineEdit, QMessageBox, QTabWidget
)

from app.repositories import cours_repository, professeurs_repository, emploi_du_temps_repository
from app.ui.cours_form_dialog import CoursFormDialog

JOURS_AFFICHAGE = {
    "lundi": "Lundi", "mardi": "Mardi", "mercredi": "Mercredi",
    "jeudi": "Jeudi", "vendredi": "Vendredi", "samedi": "Samedi",
}


class CoursProfWidget(QWidget):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self.professeur = professeurs_repository.obtenir_professeur_par_user_id(user_id)
        self._construire_interface()

    def _construire_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        titre = QLabel("Mes cours et emploi du temps")
        titre.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(titre)

        onglets = QTabWidget()
        onglets.addTab(self._construire_onglet_cours(), "Mes cours")
        onglets.addTab(self._construire_onglet_emploi_du_temps(), "Emploi du temps")
        layout.addWidget(onglets)

    def _construire_onglet_cours(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(12, 12, 12, 12)

        entete = QHBoxLayout()
        entete.addStretch()
        bouton_ajouter = QPushButton("+ Ajouter un cours")
        bouton_ajouter.setStyleSheet(
            "background-color: #2563eb; color: white; font-weight: bold; padding: 6px 12px;"
        )
        bouton_ajouter.clicked.connect(self._ouvrir_formulaire_cours)
        entete.addWidget(bouton_ajouter)
        layout.addLayout(entete)

        self.tableau_cours = QTableWidget()
        colonnes = ["Titre", "Classe", "Description", "PDF", "Date"]
        self.tableau_cours.setColumnCount(len(colonnes))
        self.tableau_cours.setHorizontalHeaderLabels(colonnes)
        self.tableau_cours.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableau_cours.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableau_cours.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        layout.addWidget(self.tableau_cours)

        if self.professeur is None:
            label = QLabel("Aucun profil professeur associe a ce compte. Contactez l'administration.")
            label.setStyleSheet("color: #888; font-style: italic;")
            layout.addWidget(label)

        self._rafraichir_cours()
        return page

    def _construire_onglet_emploi_du_temps(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        formulaire_ajout = QHBoxLayout()

        self.champ_classe_edt = QComboBox()
        classes = professeurs_repository.lister_classes_du_professeur(self.professeur["id"]) if self.professeur else []
        for c in classes:
            self.champ_classe_edt.addItem(c["nom"], userData=c["id"])
        formulaire_ajout.addWidget(self.champ_classe_edt)

        self.champ_jour = QComboBox()
        for cle, libelle in JOURS_AFFICHAGE.items():
            self.champ_jour.addItem(libelle, userData=cle)
        formulaire_ajout.addWidget(self.champ_jour)

        self.champ_heure_debut = QLineEdit()
        self.champ_heure_debut.setPlaceholderText("08:00")
        self.champ_heure_debut.setMaximumWidth(70)
        formulaire_ajout.addWidget(self.champ_heure_debut)

        self.champ_heure_fin = QLineEdit()
        self.champ_heure_fin.setPlaceholderText("09:00")
        self.champ_heure_fin.setMaximumWidth(70)
        formulaire_ajout.addWidget(self.champ_heure_fin)

        self.champ_matiere = QLineEdit()
        self.champ_matiere.setPlaceholderText("Matiere")
        formulaire_ajout.addWidget(self.champ_matiere)

        bouton_ajouter_creneau = QPushButton("Ajouter")
        bouton_ajouter_creneau.clicked.connect(self._ajouter_creneau)
        formulaire_ajout.addWidget(bouton_ajouter_creneau)

        layout.addLayout(formulaire_ajout)

        self.label_erreur_edt = QLabel("")
        self.label_erreur_edt.setStyleSheet("color: #c0392b;")
        layout.addWidget(self.label_erreur_edt)

        self.tableau_edt = QTableWidget()
        colonnes_edt = ["Jour", "Debut", "Fin", "Matiere", "Classe"]
        self.tableau_edt.setColumnCount(len(colonnes_edt))
        self.tableau_edt.setHorizontalHeaderLabels(colonnes_edt)
        self.tableau_edt.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tableau_edt)

        self._rafraichir_emploi_du_temps()
        return page

    def _ouvrir_formulaire_cours(self):
        dialogue = CoursFormDialog(user_id=self.user_id, parent=self)
        if dialogue.exec() == CoursFormDialog.Accepted:
            self._rafraichir_cours()

    def _rafraichir_cours(self):
        if self.professeur is None:
            self.tableau_cours.setRowCount(0)
            return
        cours = cours_repository.lister_cours_du_professeur(self.professeur["id"])
        from app.repositories import classes_repository
        noms_classes = {c["id"]: c["nom"] for c in classes_repository.lister_classes()}

        self.tableau_cours.setRowCount(len(cours))
        for ligne, c in enumerate(cours):
            self.tableau_cours.setItem(ligne, 0, QTableWidgetItem(c["titre"]))
            self.tableau_cours.setItem(ligne, 1, QTableWidgetItem(noms_classes.get(c["classe_id"], "?")))
            self.tableau_cours.setItem(ligne, 2, QTableWidgetItem(c.get("description") or ""))
            self.tableau_cours.setItem(ligne, 3, QTableWidgetItem("Oui" if c.get("fichier_pdf") else "Non"))
            self.tableau_cours.setItem(ligne, 4, QTableWidgetItem((c.get("date_creation") or "")[:10]))

    def _ajouter_creneau(self):
        if self.professeur is None:
            self.label_erreur_edt.setText("Aucun profil professeur associe.")
            return

        classe_id = self.champ_classe_edt.currentData()
        jour = self.champ_jour.currentData()
        heure_debut = self.champ_heure_debut.text().strip()
        heure_fin = self.champ_heure_fin.text().strip()
        matiere = self.champ_matiere.text().strip()

        import re
        motif_heure = r"^\d{2}:\d{2}$"
        if not re.match(motif_heure, heure_debut) or not re.match(motif_heure, heure_fin):
            self.label_erreur_edt.setText("Les heures doivent etre au format HH:MM (ex: 08:00).")
            return
        if not matiere:
            self.label_erreur_edt.setText("La matiere est obligatoire.")
            return
        if heure_fin <= heure_debut:
            self.label_erreur_edt.setText("L'heure de fin doit etre apres l'heure de debut.")
            return

        try:
            emploi_du_temps_repository.ajouter_creneau(
                self.professeur["id"], classe_id, jour, heure_debut, heure_fin, matiere
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur technique", f"Impossible d'ajouter le creneau : {e}")
            return

        self.label_erreur_edt.setText("")
        self.champ_matiere.clear()
        self._rafraichir_emploi_du_temps()

    def _rafraichir_emploi_du_temps(self):
        if self.professeur is None:
            self.tableau_edt.setRowCount(0)
            return
        creneaux = emploi_du_temps_repository.lister_creneaux_du_professeur(self.professeur["id"])
        from app.repositories import classes_repository
        noms_classes = {c["id"]: c["nom"] for c in classes_repository.lister_classes()}

        self.tableau_edt.setRowCount(len(creneaux))
        for ligne, c in enumerate(creneaux):
            self.tableau_edt.setItem(ligne, 0, QTableWidgetItem(JOURS_AFFICHAGE.get(c["jour"], c["jour"])))
            self.tableau_edt.setItem(ligne, 1, QTableWidgetItem(c["heure_debut"]))
            self.tableau_edt.setItem(ligne, 2, QTableWidgetItem(c["heure_fin"]))
            self.tableau_edt.setItem(ligne, 3, QTableWidgetItem(c["matiere"]))
            self.tableau_edt.setItem(ligne, 4, QTableWidgetItem(noms_classes.get(c["classe_id"], "?")))
