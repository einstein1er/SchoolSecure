"""
Genere un jeu de donnees de test realiste :
- 3 classes
- 15 eleves repartis dessus
- historique de paiements varie (soldes / partiels / non payes)
- 2 comptes utilisateurs de test

Usage (racine du projet, venv actif) :
    python seed_data.py

Peut etre relance plusieurs fois sans tout dupliquer : il verifie
d'abord si les classes/utilisateurs existent deja.
"""

import random
from app.repositories import classes_repository, users_repository, eleves_repository, paiements_repository

ANNEE_SCOLAIRE = "2025-2026"

ELEVES_DATA = [
    ("DIALLO", "Fatou"), ("KONE", "Ibrahim"), ("TRAORE", "Awa"),
    ("CAMARA", "Mohamed"), ("BAH", "Mariam"), ("SYLLA", "Ousmane"),
    ("KEITA", "Aissatou"), ("COULIBALY", "Sekou"), ("SANGARE", "Kadiatou"),
    ("TOURE", "Boubacar"), ("CISSE", "Fanta"), ("DOUMBIA", "Lassana"),
    ("FOFANA", "Hawa"), ("SIDIBE", "Moussa"), ("BARRY", "Aminata"),
]


def recuperer_ou_creer_classes():
    classes = classes_repository.lister_classes(ANNEE_SCOLAIRE)
    if len(classes) >= 3:
        return [c["id"] for c in classes[:3]]

    ids = []
    for nom, niveau in [("6eme A", "6eme"), ("5eme B", "5eme"), ("4eme C", "4eme")]:
        ids.append(classes_repository.creer_classe(nom, niveau, ANNEE_SCOLAIRE))
    return ids


def recuperer_ou_creer_utilisateur_test(username, role, nom_complet):
    existants = users_repository.lister_utilisateurs_par_role(role)
    for u in existants:
        if u["username"] == username:
            return u["id"]
    return users_repository.creer_utilisateur(username, "test1234", role, nom_complet)


def generer_eleves_et_paiements(classe_ids, enregistre_par):
    for i, (nom, prenom) in enumerate(ELEVES_DATA):
        classe_id = classe_ids[i % len(classe_ids)]
        total_du = random.choice([100000, 125000, 150000])
        eleve_id = eleves_repository.ajouter_eleve(nom, prenom, classe_id, ANNEE_SCOLAIRE, total_du)

        # Creation du compte de connexion de l'eleve (role 'eleve')
        # Identifiant simple : prenom.nom en minuscules (unique pour ce jeu de test)
        username_eleve = f"{prenom.lower()}.{nom.lower()}"
        user_eleve_id = users_repository.creer_utilisateur(
            username_eleve, "eleve1234", "eleve", f"{prenom} {nom}"
        )
        eleves_repository.associer_compte_utilisateur(eleve_id, user_eleve_id)

        # Repartition volontaire : 5 soldes / 5 partiels / 5 non payes
        groupe = i % 3

        if groupe == 0:
            # Solde : un ou deux versements qui couvrent tout
            if random.random() < 0.5:
                paiements_repository.enregistrer_paiement(eleve_id, total_du, "mobile_money", enregistre_par)
            else:
                moitie = total_du // 2
                paiements_repository.enregistrer_paiement(eleve_id, moitie, "especes", enregistre_par)
                paiements_repository.enregistrer_paiement(eleve_id, total_du - moitie, "virement", enregistre_par)

        elif groupe == 1:
            # Partiellement paye : un versement partiel
            montant_partiel = int(total_du * random.choice([0.3, 0.4, 0.6]))
            mode = random.choice(["especes", "cheque", "mobile_money"])
            paiements_repository.enregistrer_paiement(eleve_id, montant_partiel, mode, enregistre_par)

        # groupe == 2 : non paye, on ne fait rien

        print(f"Eleve cree : {prenom} {nom} (classe_id={classe_id}, total_du={total_du}, "
              f"groupe={['solde','partiel','non_paye'][groupe]}) | login: {username_eleve} / eleve1234")


def main():
    print("--- Creation des classes ---")
    classe_ids = recuperer_ou_creer_classes()
    print("Classes :", classe_ids)

    print("\n--- Creation des utilisateurs de test ---")
    secretaire_id = recuperer_ou_creer_utilisateur_test("secretaire_test", "secretariat", "Ama KOSSI")
    comptable_id = recuperer_ou_creer_utilisateur_test("comptable_test", "comptabilite", "Yao MENSAH")
    directeur_id = recuperer_ou_creer_utilisateur_test("directeur_test", "super_admin", "Kokou ADJOVI")
    print(f"secretaire_test (id={secretaire_id}) / mot de passe : test1234")
    print(f"comptable_test (id={comptable_id}) / mot de passe : test1234")
    print(f"directeur_test (id={directeur_id}) / mot de passe : test1234")

    print("\n--- Creation des eleves et paiements ---")
    generer_eleves_et_paiements(classe_ids, enregistre_par=secretaire_id)

    print("\nJeu de donnees genere avec succes.")


if __name__ == "__main__":
    main()
