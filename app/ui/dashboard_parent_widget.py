"""
Dashboard parent (lecture seule) : affiche, pour chaque enfant lie au
compte parent connecte, ses infos de base, son solde et son statut de
paiement. Aucune action possible (pas de modification, pas de paiement) --
strictement une vue de suivi.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtGui import QColor

from app.repositories import parents_eleves_repository, classes_repository
from app.business.eleve_service import fiche_complete_eleve

COULEURS_STATUT = {
    "Solde": QColor("#16a34a"),
    "Partiellement paye": QColor("#d97706"),
    "Non paye": QColor("#dc2626"),
}


class DashboardParentWidget(QWidget):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        self._construire_interface()

    def _construire_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        titre = QLabel("Suivi de mes enfants")
        titre.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(titre)

        ids_enfants = parents_eleves_repository.lister_enfants_ids(self.user_id)

        if not ids_enfants:
            label = QLabel(
                "Aucun enfant n'est associe a ce compte pour le moment. "
                "Contactez le secretariat de l'etablissement pour faire le lien."
            )
            label.setStyleSheet("color: #888; font-style: italic;")
            label.setWordWrap(True)
            layout.addWidget(label)
            return

        for eleve_id in ids_enfants:
            layout.addWidget(self._carte_enfant(eleve_id))

        layout.addStretch()

        note = QLabel("Cette page est en lecture seule. Pour toute question, contactez le secretariat.")
        note.setStyleSheet("color: #888; font-size: 11px; margin-top: 8px;")
        layout.addWidget(note)

    def _carte_enfant(self, eleve_id: int) -> QWidget:
        fiche = fiche_complete_eleve(eleve_id)
        classe = classes_repository.obtenir_classe(fiche["classe_id"])
        nom_classe = classe["nom"] if classe else "?"

        carte = QFrame()
        carte.setStyleSheet(
            "QFrame { background-color: #f8fafc; border: 1px solid #e2e8f0; "
            "border-radius: 6px; padding: 4px; }"
        )
        layout_carte = QVBoxLayout(carte)
        layout_carte.setContentsMargins(16, 14, 16, 14)
        layout_carte.setSpacing(6)

        nom_label = QLabel(f"{fiche['prenom']} {fiche['nom']}")
        nom_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout_carte.addWidget(nom_label)

        infos_label = QLabel(f"Classe : {nom_classe}   |   Annee scolaire : {fiche['annee_scolaire']}")
        infos_label.setStyleSheet("color: #555;")
        layout_carte.addWidget(infos_label)

        ligne_montants = QHBoxLayout()
        ligne_montants.addWidget(self._mini_bloc("Total du", f"{fiche['total_du']:,.0f} FCFA".replace(",", " ")))
        ligne_montants.addWidget(self._mini_bloc("Total paye", f"{fiche['total_paye']:,.0f} FCFA".replace(",", " ")))
        ligne_montants.addWidget(self._mini_bloc("Solde restant", f"{fiche['solde']:,.0f} FCFA".replace(",", " ")))

        couleur_statut = COULEURS_STATUT.get(fiche["statut"], QColor("#000")).name()
        statut_label = QLabel(fiche["statut"])
        statut_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {couleur_statut};")
        bloc_statut = QVBoxLayout()
        libelle_statut = QLabel("Statut")
        libelle_statut.setStyleSheet("color: #888; font-size: 11px;")
        bloc_statut.addWidget(libelle_statut)
        bloc_statut.addWidget(statut_label)
        conteneur_statut = QWidget()
        conteneur_statut.setLayout(bloc_statut)
        ligne_montants.addWidget(conteneur_statut)

        layout_carte.addLayout(ligne_montants)
        return carte

    def _mini_bloc(self, libelle_text: str, valeur_text: str) -> QWidget:
        bloc = QVBoxLayout()
        libelle = QLabel(libelle_text)
        libelle.setStyleSheet("color: #888; font-size: 11px;")
        valeur = QLabel(valeur_text)
        valeur.setStyleSheet("font-size: 14px; font-weight: bold;")
        bloc.addWidget(libelle)
        bloc.addWidget(valeur)
        conteneur = QWidget()
        conteneur.setLayout(bloc)
        return conteneur
