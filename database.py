# database.py
import sqlite3
from pathlib import Path

DB_NAME = "cafe.db"

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    """Création automatique de la base de données + données de départ."""
    new_db = not Path(DB_NAME).exists()
    conn = get_conn()
    c = conn.cursor()

    # Utilisateurs (serveurs)
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    # Catégories
    c.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)

    # Produits
    c.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        category_id INTEGER,
        FOREIGN KEY(category_id) REFERENCES categories(id)
    )
    """)

    # Commandes
    c.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        serveur_id INTEGER,
        total REAL,
        date TEXT,
        FOREIGN KEY(serveur_id) REFERENCES users(id)
    )
    """)

    # Détails commandes
    c.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        qty INTEGER,
        price REAL,
        FOREIGN KEY(order_id) REFERENCES orders(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)

    # Paramètres (nom du café)
    c.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cafe_name TEXT NOT NULL
    )
    """)

    # Si la base est nouvelle → نزيدو الداتا ديال البداية
    if new_db:
        # Users (serveurs)
        c.executemany(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            [
                ("ali", "1234", "serveur"),
                ("hamid", "5678", "serveur"),
                ("admin", "admin", "admin"),
            ]
        )

        # Catégories
        c.executemany(
            "INSERT INTO categories (name) VALUES (?)",
            [
                ("Petit déjeuner",),
                ("Déjeuner",),
                ("Café",),
                ("Jus",),
                ("Dessert",),
            ]
        )

        # Récupérer les ids des catégories
        c.execute("SELECT id, name FROM categories")
        cat_map = {name: cid for cid, name in c.fetchall()}

        # Produits
        c.executemany(
            "INSERT INTO products (name, price, category_id) VALUES (?, ?, ?)",
            [
                ("Café", 10, cat_map["Café"]),
                ("Cappuccino", 14, cat_map["Café"]),
                ("Thé", 8, cat_map["Café"]),
                ("Café au lait", 11, cat_map["Café"]),

                ("Jus d'orange", 12, cat_map["Jus"]),
                ("Jus de citron", 11, cat_map["Jus"]),

                ("Croissant", 5, cat_map["Petit déjeuner"]),
                ("Msemen", 7, cat_map["Petit déjeuner"]),

                ("Tacos poulet", 22, cat_map["Déjeuner"]),
                ("Panini fromage", 20, cat_map["Déjeuner"]),

                ("Gâteau au chocolat", 15, cat_map["Dessert"]),
            ]
        )

    c.execute("SELECT COUNT(*) FROM settings")
    row = c.fetchone()
    if not row or row[0] == 0:
        c.execute(
            "INSERT INTO settings (cafe_name) VALUES (?)",
            ("Café Caisse Manager",),
        )

    conn.commit()
    conn.close()
