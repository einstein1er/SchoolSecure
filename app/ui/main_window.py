"""
Fenetre principale avec menu lateral dynamique.

Principe de structure : chaque entree de menu correspond a un
"screen_id". Pour l'instant, chaque screen_id affiche une page
provisoire (QLabel "a venir"). Aux prochaines etapes, on remplacera
juste l'entree correspondante par le vrai widget (ex: EleveListWidget)
-- rien d'autre ne change dans cette classe.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
    QStackedWidget, QFrame
)
from PySide6.QtCore import Signal, Qt

from app.ui.eleves_liste_widget import ElevesListeWidget

# Ecrans reellement codes : screen_id -> fonction qui construit le widget.
# Un screen_id absent de ce dictionnaire affiche automatiquement la page
# provisoire "a venir". Pour brancher un nouvel ecran plus tard, il suffit
# d'ajouter une ligne ici, rien d'autre a changer dans cette classe.
ECRANS_REELS = {
    "eleves_liste": lambda utilisateur: ElevesListeWidget(
        role=utilisateur["role"], utilisateur_id=utilisateur["id"]
    ),
}

NOMS_ROLES = {
    "super_admin": "Super Administrateur (Directeur)",
    "secretariat": "Secretariat",
    "comptabilite": "Comptabilite",
    "rh": "Ressources Humaines",
    "professeur": "Professeur",
    "eleve": "Eleve",
    "parent": "Parent",
}

# Menu affiche selon le role connecte : liste de (libelle affiche, screen_id)
MENUS_PAR_ROLE = {
    "super_admin": [
        ("Tableau de bord", "tableau_de_bord"),
        ("Eleves", "eleves_liste"),
        ("Paiements", "paiements"),
        ("Classes", "classes"),
        ("Comptes utilisateurs", "comptes"),
        ("Professeurs", "professeurs"),
        ("Ressources Humaines", "rh"),
        ("Journal d'audit", "audit"),
    ],
    "secretariat": [
        ("Tableau de bord", "tableau_de_bord"),
        ("Eleves", "eleves_liste"),
        ("Classes", "classes"),
    ],
    "comptabilite": [
        ("Tableau de bord", "tableau_de_bord"),
        ("Paiements", "paiements"),
        ("Eleves", "eleves_liste"),
    ],
    "rh": [
        ("Tableau de bord", "tableau_de_bord"),
        ("Employes", "rh"),
    ],
    "professeur": [
        ("Tableau de bord", "tableau_de_bord"),
        ("Mes cours", "mes_cours"),
        ("Mes eleves", "mes_eleves"),
        ("Emploi du temps", "emploi_du_temps"),
    ],
    "eleve": [
        ("Mon tableau de bord", "tableau_de_bord"),
        ("Mes cours", "mes_cours_eleve"),
        ("Mes paiements", "mes_paiements"),
    ],
    "parent": [
        ("Tableau de bord", "tableau_de_bord"),
        ("Suivi de mon enfant", "suivi_enfant"),
    ],
}


def _page_provisoire(libelle: str) -> QWidget:
    """Page temporaire affichee tant que l'ecran reel n'est pas code."""
    page = QWidget()
    layout = QVBoxLayout(page)
    label = QLabel(f"Ecran \u00ab {libelle} \u00bb \u2014 a venir")
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("color: #888; font-size: 16px;")
    layout.addWidget(label)
    return page


class MainWindow(QWidget):
    deconnexion_demandee = Signal()

    def __init__(self, utilisateur: dict):
        super().__init__()
        self.utilisateur = utilisateur
        self.setWindowTitle("Gestion Scolaire")
        self.setMinimumSize(900, 600)

        self.pages_par_screen_id = {}   # screen_id -> index dans le QStackedWidget
        self.boutons_menu = []

        self._construire_interface()

    def _construire_interface(self):
        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # --- Barre laterale ---
        barre_laterale = QFrame()
        barre_laterale.setFixedWidth(220)
        barre_laterale.setStyleSheet("background-color: #1e293b;")
        layout_barre = QVBoxLayout(barre_laterale)
        layout_barre.setContentsMargins(0, 16, 0, 16)
        layout_barre.setSpacing(4)

        nom_role = NOMS_ROLES.get(self.utilisateur["role"], self.utilisateur["role"])
        entete = QLabel(f"{self.utilisateur['nom_complet']}\n{nom_role}")
        entete.setStyleSheet("color: white; font-weight: bold; padding: 12px 16px;")
        entete.setWordWrap(True)
        layout_barre.addWidget(entete)

        menu_items = MENUS_PAR_ROLE.get(self.utilisateur["role"], [])
        self.zone_contenu = QStackedWidget()

        for libelle, screen_id in menu_items:
            bouton = QPushButton(libelle)
            bouton.setCheckable(True)
            bouton.setStyleSheet(self._style_bouton_menu())
            bouton.clicked.connect(lambda checked, sid=screen_id: self._afficher_page(sid))
            layout_barre.addWidget(bouton)
            self.boutons_menu.append((screen_id, bouton))

            if screen_id in ECRANS_REELS:
                page = ECRANS_REELS[screen_id](self.utilisateur)
            else:
                page = _page_provisoire(libelle)
            index = self.zone_contenu.addWidget(page)
            self.pages_par_screen_id[screen_id] = index

        layout_barre.addStretch()

        bouton_deconnexion = QPushButton("Se deconnecter")
        bouton_deconnexion.setStyleSheet(
            "QPushButton { color: #f87171; background: transparent; border: none; "
            "padding: 12px 16px; text-align: left; } "
            "QPushButton:hover { background-color: #334155; }"
        )
        bouton_deconnexion.clicked.connect(self.deconnexion_demandee.emit)
        layout_barre.addWidget(bouton_deconnexion)

        layout_principal.addWidget(barre_laterale)
        layout_principal.addWidget(self.zone_contenu, stretch=1)

        # Ouvre la premiere page du menu par defaut
        if menu_items:
            self._afficher_page(menu_items[0][1])

    def _style_bouton_menu(self) -> str:
        return (
            "QPushButton { color: #e2e8f0; background: transparent; border: none; "
            "padding: 12px 16px; text-align: left; font-size: 14px; } "
            "QPushButton:hover { background-color: #334155; } "
            "QPushButton:checked { background-color: #2563eb; color: white; font-weight: bold; }"
        )

    def _afficher_page(self, screen_id: str):
        index = self.pages_par_screen_id.get(screen_id)
        if index is not None:
            self.zone_contenu.setCurrentIndex(index)
        # Met a jour l'etat visuel "coche" du bouton actif
        for sid, bouton in self.boutons_menu:
            bouton.setChecked(sid == screen_id)
