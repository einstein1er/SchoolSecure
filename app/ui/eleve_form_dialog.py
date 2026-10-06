"""
Formulaire d'ajout/modification d'un eleve.

Regle d'acces (version simple, en attendant le vrai systeme de
permissions configurables sur la branche gestion_permission) :
- Creation : secretariat ET super_admin peuvent saisir nom/telephone parent
- Modification : SEUL super_admin voit et peut modifier nom/telephone parent.
  Pour les autres roles autorises a modifier un eleve (secretariat), ces
  deux champs sont totalement absents du formulaire d'edition, pour eviter
  qu'un enregistrement n'ecrase par erreur une donnee qu'ils ne voient pas.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout, QLineEdit, QComboBox,
    QPushButton, QLabel, QMessageBox
)
from PySide6.QtCore import Qt

from app.repositories import classes_repository, eleves_repository, permissions_repository
from app.business.soldes import MontantInvalideError


class EleveFormDialog(QDialog):
    def __init__(self, role: str, eleve_id: int = None, utilisateur_id: int = None, parent=None):
        """role : role de l'utilisateur connecte (controle l'acces aux
        champs parent). eleve_id : None pour un ajout, un id pour une
        modification."""
        super().__init__(parent)
        self.role = role
        self.utilisateur_id = utilisateur_id
        self.eleve_id = eleve_id
        self.mode_edition = eleve_id is not None
        self.eleve_existant = eleves_repository.obtenir_eleve(eleve_id) if self.mode_edition else None

        # Creation : toujours autorise (saisie initiale, pas de risque d'ecraser
        # une donnee existante qu'on ne voit pas). Modification : depend de la
        # permission configurable par le directeur (super_admin toujours vrai).
        self.afficher_champs_parent = (
            not self.mode_edition or permissions_repository.autorise(self.role, "voir_infos_parent")
        )

        self.setWindowTitle("Modifier un eleve" if self.mode_edition else "Ajouter un eleve")
        self.setMinimumWidth(420)
        self._construire_interface()
        if self.mode_edition:
            self._pre_remplir()

    def _construire_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        titre = QLabel("Modifier un eleve" if self.mode_edition else "Ajouter un eleve")
        titre.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(titre)

        formulaire = QFormLayout()
        formulaire.setSpacing(10)

        if self.mode_edition:
            label_matricule = QLabel(self.eleve_existant["matricule"])
            label_matricule.setStyleSheet("color: #555;")
            formulaire.addRow("Matricule :", label_matricule)

        self.champ_nom = QLineEdit()
        formulaire.addRow("Nom * :", self.champ_nom)

        self.champ_prenom = QLineEdit()
        formulaire.addRow("Prenom * :", self.champ_prenom)

        self.champ_classe = QComboBox()
        for c in classes_repository.lister_classes():
            self.champ_classe.addItem(c["nom"], userData=c["id"])
        formulaire.addRow("Classe * :", self.champ_classe)

        self.champ_annee_scolaire = QLineEdit("2025-2026")
        formulaire.addRow("Annee scolaire * :", self.champ_annee_scolaire)

        self.champ_total_du = QLineEdit()
        self.champ_total_du.setPlaceholderText("ex: 150000")
        formulaire.addRow("Total frais dus (FCFA) * :", self.champ_total_du)

        self.champ_date_naissance = QLineEdit()
        self.champ_date_naissance.setPlaceholderText("AAAA-MM-JJ (optionnel)")
        formulaire.addRow("Date de naissance :", self.champ_date_naissance)

        self.champ_sexe = QComboBox()
        self.champ_sexe.addItem("Non precise", userData=None)
        self.champ_sexe.addItem("Masculin", userData="M")
        self.champ_sexe.addItem("Feminin", userData="F")
        formulaire.addRow("Sexe :", self.champ_sexe)

        if self.afficher_champs_parent:
            self.champ_nom_parent = QLineEdit()
            formulaire.addRow("Nom du parent/tuteur :", self.champ_nom_parent)

            self.champ_telephone_parent = QLineEdit()
            formulaire.addRow("Telephone du parent :", self.champ_telephone_parent)
        else:
            self.champ_nom_parent = None
            self.champ_telephone_parent = None
            note_restriction = QLabel("🔒 Les coordonnees du parent sont reservees au directeur.")
            note_restriction.setStyleSheet("color: #888; font-style: italic;")
            note_restriction.setWordWrap(True)
            formulaire.addRow(note_restriction)

        layout.addLayout(formulaire)

        self.label_erreur = QLabel("")
        self.label_erreur.setStyleSheet("color: #c0392b;")
        self.label_erreur.setWordWrap(True)
        layout.addWidget(self.label_erreur)

        boutons = QHBoxLayout()
        bouton_annuler = QPushButton("Annuler")
        bouton_annuler.clicked.connect(self.reject)
        boutons.addWidget(bouton_annuler)

        bouton_enregistrer = QPushButton("Modifier" if self.mode_edition else "Ajouter")
        bouton_enregistrer.setDefault(True)
        bouton_enregistrer.clicked.connect(self._enregistrer)
        boutons.addWidget(bouton_enregistrer)

        layout.addLayout(boutons)

    def _pre_remplir(self):
        e = self.eleve_existant
        self.champ_nom.setText(e["nom"])
        self.champ_prenom.setText(e["prenom"])
        index_classe = self.champ_classe.findData(e["classe_id"])
        if index_classe >= 0:
            self.champ_classe.setCurrentIndex(index_classe)
        self.champ_annee_scolaire.setText(e["annee_scolaire"])
        self.champ_total_du.setText(str(int(e["total_du"])))
        self.champ_date_naissance.setText(e.get("date_naissance") or "")
        index_sexe = self.champ_sexe.findData(e.get("sexe"))
        if index_sexe >= 0:
            self.champ_sexe.setCurrentIndex(index_sexe)

        if self.afficher_champs_parent:
            self.champ_nom_parent.setText(e.get("nom_parent") or "")
            self.champ_telephone_parent.setText(e.get("telephone_parent") or "")

    def _valider_champs(self) -> dict | None:
        """Retourne un dict de valeurs validees, ou None si invalide
        (le message d'erreur est deja affiche dans ce cas)."""
        nom = self.champ_nom.text().strip()
        prenom = self.champ_prenom.text().strip()
        annee_scolaire = self.champ_annee_scolaire.text().strip()
        total_du_texte = self.champ_total_du.text().strip()
        date_naissance = self.champ_date_naissance.text().strip() or None

        if not nom or not prenom or not annee_scolaire:
            self.label_erreur.setText("Les champs Nom, Prenom et Annee scolaire sont obligatoires.")
            return None

        try:
            total_du = float(total_du_texte)
        except ValueError:
            self.label_erreur.setText("Le total des frais dus doit etre un nombre (ex: 150000).")
            return None

        if total_du <= 0:
            self.label_erreur.setText("Le total des frais dus doit etre superieur a zero.")
            return None

        if date_naissance:
            import re
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_naissance):
                self.label_erreur.setText("La date de naissance doit etre au format AAAA-MM-JJ.")
                return None

        if self.mode_edition:
            total_deja_paye = self.eleve_existant["total_paye"] if "total_paye" in self.eleve_existant else None
            # Si l'info n'est pas dans eleve_existant (chargee via obtenir_eleve simple),
            # on la recalcule via le service pour etre sur.
            if total_deja_paye is None:
                from app.business.eleve_service import fiche_complete_eleve
                fiche = fiche_complete_eleve(self.eleve_id)
                total_deja_paye = fiche["total_paye"]
            if total_du < total_deja_paye:
                self.label_erreur.setText(
                    f"Impossible : cet eleve a deja paye {total_deja_paye:,.0f} FCFA. "
                    f"Le nouveau total ne peut pas etre inferieur a ce montant."
                )
                return None

        self.label_erreur.setText("")
        return {
            "nom": nom,
            "prenom": prenom,
            "classe_id": self.champ_classe.currentData(),
            "annee_scolaire": annee_scolaire,
            "total_du": total_du,
            "date_naissance": date_naissance,
            "sexe": self.champ_sexe.currentData(),
            "nom_parent": self.champ_nom_parent.text().strip() if self.champ_nom_parent else None,
            "telephone_parent": self.champ_telephone_parent.text().strip() if self.champ_telephone_parent else None,
        }

    def _enregistrer(self):
        valeurs = self._valider_champs()
        if valeurs is None:
            return

        try:
            if self.mode_edition:
                eleves_repository.modifier_eleve(
                    self.eleve_id,
                    nom=valeurs["nom"], prenom=valeurs["prenom"], classe_id=valeurs["classe_id"],
                    total_du=valeurs["total_du"], date_naissance=valeurs["date_naissance"],
                    sexe=valeurs["sexe"],
                    nom_parent=valeurs["nom_parent"], telephone_parent=valeurs["telephone_parent"],
                    modifier_champs_parent=self.afficher_champs_parent,
                    modifie_par=self.utilisateur_id,
                )
            else:
                eleves_repository.ajouter_eleve(
                    valeurs["nom"], valeurs["prenom"], valeurs["classe_id"],
                    valeurs["annee_scolaire"], valeurs["total_du"],
                    date_naissance=valeurs["date_naissance"], sexe=valeurs["sexe"],
                    nom_parent=valeurs["nom_parent"], telephone_parent=valeurs["telephone_parent"],
                    modifie_par=self.utilisateur_id,
                )
        except MontantInvalideError as e:
            self.label_erreur.setText(str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Erreur technique", f"Une erreur est survenue : {e}")
            return

        self.accept()
