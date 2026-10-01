import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.repositories import classes_repository, users_repository, eleves_repository, paiements_repository
from app.business.eleve_service import fiche_complete_eleve
from app.business.soldes import MontantInvalideError

print("--- Test 1 : creer une classe ---")
classe_id = classes_repository.creer_classe("6eme A", "6eme", "2025-2026")
print("Classe creee, id =", classe_id)

print("\n--- Test 2 : creer un utilisateur secretariat ---")
user_id = users_repository.creer_utilisateur(
    "secretaire1", "motdepasse123", "secretariat", "Ama KOSSI", "ama@ecole.tg", "+228 90 00 00 00"
)
print("Utilisateur cree, id =", user_id)

print("\n--- Test 3 : verifier les identifiants ---")
u = users_repository.verifier_identifiants("secretaire1", "motdepasse123")
print("Connexion reussie :", u)
u_faux = users_repository.verifier_identifiants("secretaire1", "mauvais_mdp")
print("Connexion avec mauvais mdp (doit etre None) :", u_faux)

print("\n--- Test 4 : ajouter un eleve ---")
eleve_id = eleves_repository.ajouter_eleve("CAMARA", "Mohamed", classe_id, "2025-2026", 150000)
print("Eleve cree, id =", eleve_id)

print("\n--- Test 5 : verifier le chiffrement en base brute ---")
import sqlite3
conn = sqlite3.connect("app/database/school.db")
row = conn.execute("SELECT nom_chiffre, prenom_chiffre, total_du_chiffre FROM eleves WHERE id = ?", (eleve_id,)).fetchone()
print("Donnees BRUTES en base (doivent etre illisibles) :", row)
conn.close()

print("\n--- Test 6 : lire l'eleve dechiffre ---")
eleve = eleves_repository.obtenir_eleve(eleve_id)
print("Eleve dechiffre :", eleve)

print("\n--- Test 7 : enregistrer un paiement valide ---")
paiement = paiements_repository.enregistrer_paiement(eleve_id, 50000, "mobile_money", user_id)
print("Paiement enregistre :", paiement)

print("\n--- Test 8 : fiche complete (solde + statut) ---")
fiche = fiche_complete_eleve(eleve_id)
print("Total du :", fiche["total_du"])
print("Total paye :", fiche["total_paye"])
print("Solde :", fiche["solde"])
print("Statut :", fiche["statut"])

print("\n--- Test 9 : paiement invalide (depasse le solde) ---")
try:
    paiements_repository.enregistrer_paiement(eleve_id, 999999, "especes", user_id)
    print("ERREUR : aurait du lever une exception !")
except MontantInvalideError as e:
    print("Exception correctement levee :", e)

print("\n--- Test 10 : second paiement qui solde le compte ---")
paiement2 = paiements_repository.enregistrer_paiement(eleve_id, 100000, "especes", user_id)
fiche2 = fiche_complete_eleve(eleve_id)
print("Solde final :", fiche2["solde"], "| Statut :", fiche2["statut"])

print("\n--- Test 11 : reimpression via numero de recu ---")
recu_retrouve = paiements_repository.obtenir_paiement_par_numero(paiement["numero_recu"])
print("Recu retrouve :", recu_retrouve)

print("\nTOUS LES TESTS SE SONT EXECUTES SANS ERREUR.")
