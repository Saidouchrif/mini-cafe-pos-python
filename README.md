# Café Caisse Manager (Python + PyQt5 + SQLite)

Application de caisse complète pour café, développée en Python 3 avec PyQt5 et SQLite.
La base `cafe.db` est créée automatiquement au premier lancement avec les tables et
les données initiales (utilisateurs, catégories, produits, paramètres).

Utilisateurs par défaut :
- **admin / admin** (rôle : administrateur)
- **ali / 1234** (rôle : serveur)
- **hamid / 5678** (rôle : serveur)

## Fonctionnalités principales
- **Écran de connexion** (authentification sur la table `users`).
- **Rôle administrateur** :
  - Tableau de bord avec 5 boutons :
    - **Gérer les serveurs** (CRUD sur les utilisateurs, avec protection du compte admin).
    - **Gérer le menu** (CRUD sur catégories et produits).
    - **Ouvrir la caisse** (accès à la fenêtre POS).
    - **Rapports** (liste des commandes entre deux dates avec total de la période et détail).
    - **Paramètres** (configuration du nom du café utilisé sur les tickets).
- **Rôle serveur** : accès direct uniquement à la **fenêtre de caisse (POS)**.
- **Fenêtre POS (caisse)** :
  - Affichage du serveur connecté.
  - Liste des catégories à gauche, produits de la catégorie au centre.
  - Panier/commande à droite : nom du produit, quantité, total de ligne et bouton "Annuler".
  - Mise à jour automatique des quantités et du total (`Total : XX.XX DH`).
- **Paiement et tickets** :
  - Insertion d'une commande dans les tables `orders` et `order_items`.
  - Génération d'un ticket de caisse officiel en texte (`ticket_<id>.txt`) en français.
  - Tentative d'impression automatique sous Windows via `os.startfile(..., "print")`.
  - Message d'information si l'impression automatique échoue.

---

## Prérequis
- Windows (recommandé pour l'impression automatique de tickets).
- Python 3.8+ installé et accessible dans le PATH.
- `pip` installé.

---

## Installation des dépendances

Dans un terminal, placez-vous dans le dossier du projet puis exécutez :

```bash
pip install -r requirements.txt
```

> Optionnel : vous pouvez d'abord créer un environnement virtuel (`python -m venv .venv`)
> puis l'activer avant d'installer les dépendances.

---

## Lancer l'application en développement

Toujours depuis le dossier du projet :

```bash
python main.py
```

La base SQLite `cafe.db` sera créée automatiquement au premier lancement avec :
- les utilisateurs par défaut (admin, ali, hamid) ;
- les catégories et produits d'exemple ;
- les paramètres avec un nom de café par défaut.

Connectez-vous ensuite avec un des comptes indiqués ci-dessus.

---

## Générer un exécutable Windows (.exe) avec PyInstaller

Assurez-vous que PyInstaller est installé (il est listé dans `requirements.txt`).
Puis, dans le dossier du projet, exécutez :

```bash
pyinstaller --onefile --windowed main.py
```

PyInstaller va créer un dossier `dist/` contenant `main.exe`. Copiez ce fichier, ainsi
que le dossier `assets/` si nécessaire, vers le poste de caisse cible. La base `cafe.db`
sera créée au premier lancement de l'exécutable si elle n'existe pas.

---

## Structure simplifiée du projet

- `main.py` : point d'entrée principal (initialisation de la base + lancement de l'UI).
- `database.py` : gestion de la base SQLite et création automatique des tables.
- `models.py` : accès aux données (utilisateurs, catégories, produits, commandes, paramètres).
- `utils/` :
  - `auth.py` : fonctions liées aux rôles (ex. vérification administrateur).
  - `tickets.py` : génération et impression des tickets de caisse.
- `ui/` :
  - `login_window.py` : écran de connexion.
  - `admin_dashboard.py` : tableau de bord administrateur.
  - `servers_window.py` : gestion des serveurs/utilisateurs.
  - `menu_window.py` : gestion des catégories et produits.
  - `pos_window.py` : interface de caisse (POS).
  - `reports_window.py` : rapports des ventes.
  - `settings_window.py` : paramètres (nom du café).

Vous pouvez adapter et étendre cette structure selon les besoins de votre café.
