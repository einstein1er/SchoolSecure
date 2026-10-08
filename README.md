# SchoolSecure — Gestion Scolaire

Application desktop multi-rôles pour la gestion scolaire : élèves, paiements, cours, emploi du temps. Développée en Python/PySide6, données sensibles chiffrées, reçus de paiement avec QR code vérifiable, 100% offline.

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation (mode développement)](#installation-mode-développement)
- [Lancer l'application](#lancer-lapplication)
- [Utiliser l'exécutable Windows (.exe)](#utiliser-lexécutable-windows-exe)
- [Comptes de test](#comptes-de-test)
- [Structure du projet](#structure-du-projet)
- [Limites connues / Roadmap](#limites-connues--roadmap)

## Fonctionnalités

- **Multi-rôles** : Directeur (super admin), Secrétariat, Comptabilité, Ressources Humaines, Professeur, Élève, Parent — chacun avec son propre menu et ses propres droits.
- **Gestion des élèves** : ajout, modification, fiche détaillée, recherche, filtre par classe, tri sur toutes les colonnes.
- **Paiements** : enregistrement avec validation stricte (impossible de dépasser le solde restant), calcul automatique du solde et du statut (Soldé / Partiellement payé / Non payé).
- **Reçus** : génération PDF avec QR code de vérification (hash signé, infalsifiable sans la clé de l'établissement).
- **Tableau de bord** : statistiques globales, liste des élèves à relancer par priorité.
- **Dashboards dédiés** : élève (ses paiements/cours), parent (suivi multi-enfants), professeur (ses élèves, ses cours, son emploi du temps).
- **Cours** : dépôt de PDF par les professeurs, consultation/téléchargement par les élèves de la classe concernée.
- **Ressources Humaines** : création de comptes (secrétariat, comptabilité, RH, professeur) avec fiche associée.
- **Permissions configurables** : le directeur ajuste dynamiquement certains droits par rôle (ex : accès aux coordonnées du parent).
- **Journal d'audit** : traçabilité des actions clés (paiements, créations/modifications d'élèves et de comptes, changements de permissions).
- **Sécurité** : chiffrement des données sensibles (Fernet/AES), mots de passe hachés (bcrypt), aucune donnée transmise sur Internet.

## Prérequis

- Python 3.10 ou supérieur
- Windows, macOS ou Linux (testé principalement sous Windows)
- Git (pour cloner le dépôt)

## Installation (mode développement)

```bash
git clone https://github.com/einstein1er/SchoolSecure.git
cd SchoolSecure

python -m venv venv
source venv/Scripts/activate      # Windows (Git Bash)
# venv\Scripts\activate.bat       # Windows (cmd)
# source venv/bin/activate        # macOS / Linux

pip install -r requirements.txt
```

## Lancer l'application

### 1. Initialiser la base de données (première fois uniquement)

```bash
python app/database/init_db.py
```

Cette commande crée `app/database/school.db` (toutes les tables) et `app/security/secret.key` (clé de chiffrement — **à sauvegarder précieusement**, sans elle les données chiffrées deviennent illisibles définitivement).

### 2. Générer un jeu de données de test (optionnel mais recommandé)

```bash
python seed_data.py
```

Crée 15+ élèves avec un historique de paiements varié (soldés, partiels, non payés), 3 classes, et un compte de test par rôle (voir [Comptes de test](#comptes-de-test)).

### 3. Lancer l'application

```bash
python main.py
```

## Utiliser l'exécutable Windows (.exe)

Un exécutable autonome peut être généré avec PyInstaller :

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name SchoolSecure main.py
```

L'exécutable est produit dans `dist/SchoolSecure.exe`.

**Important** : `school.db` et `secret.key` doivent se trouver **dans le même dossier** que l'exécutable. Au premier lancement sur une machine neuve, ces fichiers sont créés automatiquement (base vide). Pour déployer avec le jeu de données de test, copiez `app/database/school.db` et `app/security/secret.key` (générés en mode développement) à côté de `SchoolSecure.exe`.

Aucune installation de Python n'est nécessaire sur la machine de destination.

## Comptes de test

Mot de passe `test1234` pour tous les comptes administratifs (sauf élèves : `eleve1234`).

| Rôle | Identifiant |
|---|---|
| Directeur (super admin) | `directeur_test` |
| Secrétariat | `secretaire_test` |
| Comptabilité | `comptable_test` |
| Professeur (×3, un par classe) | `prof_test1`, `prof_test2`, `prof_test3` |
| Parent (2 enfants liés) | `parent_test` |
| Élève | voir la sortie de `seed_data.py` (ex : `fatou.diallo` / `eleve1234`) |

## Structure du projet

```
SchoolSecure/
├── main.py                  # Point d'entrée
├── seed_data.py              # Génération du jeu de données de test
├── requirements.txt
├── app/
│   ├── database/              # Schéma SQL, connexion, init
│   ├── security/               # Chiffrement (Fernet), clé secrète
│   ├── repositories/            # Accès aux données (1 fichier par table/domaine)
│   ├── business/                # Logique métier (soldes, validation, reçus PDF)
│   └── ui/                      # Écrans PySide6
└── fichiers_cours/             # PDF des cours déposés (généré à l'usage)
```

Architecture en couches stricte : aucun écran (`app/ui/`) n'exécute de requête SQL directement — tout passe par `app/repositories/` (accès données) et `app/business/` (règles métier).

## Limites connues / Roadmap

- Les menus **Paiements**, **Classes** et **Professeurs** (vue globale admin) sont prévus mais pas encore implémentés comme écrans autonomes — l'enregistrement de paiement se fait actuellement via la fiche élève.
- Pas de notes/bulletins ni d'exercices en ligne avec soumission (roadmap V2).
- Le module RH ne couvre pas la gestion de la paie ni des contrats (fiche basique uniquement).
- Les permissions configurables couvrent 4 droits clés ; le système est conçu pour être étendu facilement (voir `app/repositories/permissions_repository.py`).
