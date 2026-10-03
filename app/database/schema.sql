-- ============================================================
-- SCHEMA DE BASE DE DONNEES - Projet Scolaire
-- ============================================================
-- Convention : les colonnes qui finissent par "_chiffre" contiennent
-- des donnees chiffrees (texte base64 issu de Fernet/cryptography).
-- Elles ne peuvent PAS servir dans une clause WHERE ou un tri SQL :
-- on les dechiffre en Python (couche business) apres lecture.
--
-- Les colonnes SANS "_chiffre" restent en clair volontairement :
-- ce sont des identifiants, des dates, des statuts ou des cles
-- etrangeres, necessaires pour filtrer/trier/joindre efficacement.
-- ============================================================

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- 1. UTILISATEURS (login unique pour tous les roles)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    username            TEXT UNIQUE NOT NULL,
    password_hash       TEXT NOT NULL,           -- bcrypt, jamais du chiffrement reversible
    role                TEXT NOT NULL CHECK(role IN (
                            'super_admin', 'secretariat', 'comptabilite',
                            'rh', 'professeur', 'eleve', 'parent'
                        )),
    nom_complet_chiffre TEXT NOT NULL,            -- chiffre : nom + prenom du titulaire du compte
    email_chiffre       TEXT,                     -- chiffre
    telephone_chiffre   TEXT,                     -- chiffre
    actif               INTEGER NOT NULL DEFAULT 1,
    date_creation       TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ------------------------------------------------------------
-- 2. CLASSES
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS classes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nom             TEXT NOT NULL,          -- ex: "6eme A"
    niveau          TEXT,                   -- ex: "6eme"
    annee_scolaire  TEXT NOT NULL           -- ex: "2025-2026"
);

-- ------------------------------------------------------------
-- 3. ELEVES
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS eleves (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    matricule               TEXT UNIQUE NOT NULL,   -- genere automatiquement, ex: ELV-2026-001
    nom_chiffre              TEXT NOT NULL,       -- chiffre
    prenom_chiffre           TEXT NOT NULL,       -- chiffre
    classe_id                INTEGER NOT NULL,
    annee_scolaire           TEXT NOT NULL,
    total_du_chiffre         TEXT NOT NULL,       -- chiffre (montant sensible)
    date_naissance           TEXT,                -- format AAAA-MM-JJ, optionnel, en clair (peu sensible)
    sexe                     TEXT CHECK(sexe IN ('M', 'F') OR sexe IS NULL),
    nom_parent_chiffre       TEXT,                -- chiffre, acces restreint (directeur) en modification
    telephone_parent_chiffre TEXT,                -- chiffre, acces restreint (directeur) en modification
    user_id                  INTEGER,             -- NULL si l'eleve n'a pas encore de compte
    date_creation            TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (classe_id) REFERENCES classes(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ------------------------------------------------------------
-- 4. LIEN PARENT <-> ELEVE (un parent peut avoir plusieurs enfants)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS parents_eleves (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_user_id  INTEGER NOT NULL,
    eleve_id        INTEGER NOT NULL,
    FOREIGN KEY (parent_user_id) REFERENCES users(id),
    FOREIGN KEY (eleve_id) REFERENCES eleves(id),
    UNIQUE(parent_user_id, eleve_id)
);

-- ------------------------------------------------------------
-- 5. PAIEMENTS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS paiements (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    eleve_id            INTEGER NOT NULL,
    montant_chiffre     TEXT NOT NULL,       -- chiffre
    date_paiement       TEXT NOT NULL,       -- en clair : necessaire pour trier/filtrer
    mode_paiement       TEXT NOT NULL CHECK(mode_paiement IN (
                            'especes', 'cheque', 'virement', 'mobile_money'
                        )),
    numero_recu         TEXT UNIQUE NOT NULL,   -- numero unique, sert de reference publique
    solde_apres_chiffre TEXT NOT NULL,       -- chiffre : solde restant apres ce paiement
    qr_hash             TEXT NOT NULL,       -- hash de verification encode dans le QR code
    enregistre_par      INTEGER NOT NULL,    -- user_id de la personne qui a saisi le paiement
    date_creation       TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (eleve_id) REFERENCES eleves(id),
    FOREIGN KEY (enregistre_par) REFERENCES users(id)
);

-- ------------------------------------------------------------
-- 6. PROFESSEURS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS professeurs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL UNIQUE,
    specialite      TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ------------------------------------------------------------
-- 7. COURS (depots PDF par un professeur)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cours (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    professeur_id   INTEGER NOT NULL,
    classe_id       INTEGER NOT NULL,
    titre           TEXT NOT NULL,
    description     TEXT,
    fichier_pdf     TEXT,               -- chemin relatif vers le PDF stocke localement
    date_creation   TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (professeur_id) REFERENCES professeurs(id),
    FOREIGN KEY (classe_id) REFERENCES classes(id)
);

-- ------------------------------------------------------------
-- 8. EXERCICES (lies a un cours)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS exercices (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    cours_id        INTEGER NOT NULL,
    titre           TEXT NOT NULL,
    description     TEXT,
    fichier_pdf     TEXT,
    date_limite     TEXT,
    date_creation   TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (cours_id) REFERENCES cours(id)
);

-- ------------------------------------------------------------
-- 9. EMPLOI DU TEMPS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS emploi_du_temps (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    professeur_id   INTEGER NOT NULL,
    classe_id       INTEGER NOT NULL,
    jour            TEXT NOT NULL CHECK(jour IN (
                        'lundi','mardi','mercredi','jeudi','vendredi','samedi'
                    )),
    heure_debut     TEXT NOT NULL,   -- format "HH:MM"
    heure_fin       TEXT NOT NULL,
    matiere         TEXT NOT NULL,
    FOREIGN KEY (professeur_id) REFERENCES professeurs(id),
    FOREIGN KEY (classe_id) REFERENCES classes(id)
);

-- ------------------------------------------------------------
-- 10. EMPLOYES RH (personnel hors enseignants)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS employes_rh (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL UNIQUE,
    poste               TEXT NOT NULL,
    departement         TEXT NOT NULL,
    date_embauche       TEXT,
    salaire_chiffre     TEXT,        -- chiffre : tres sensible
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ------------------------------------------------------------
-- 11. JOURNAL D'AUDIT (tracabilite)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    action          TEXT NOT NULL,        -- ex: "CREATION", "MODIFICATION", "SUPPRESSION"
    table_concernee TEXT NOT NULL,
    enregistrement_id INTEGER,
    details         TEXT,
    date_action     TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ------------------------------------------------------------
-- INDEX utiles pour les recherches/filtres frequents
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_eleves_classe ON eleves(classe_id);
CREATE INDEX IF NOT EXISTS idx_paiements_eleve ON paiements(eleve_id);
CREATE INDEX IF NOT EXISTS idx_paiements_date ON paiements(date_paiement);
CREATE INDEX IF NOT EXISTS idx_cours_classe ON cours(classe_id);
CREATE INDEX IF NOT EXISTS idx_emploi_classe ON emploi_du_temps(classe_id);
