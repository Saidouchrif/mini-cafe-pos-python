from database import get_conn

def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    # Table products
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL
    )
    """)

    # Table sales
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        total REAL NOT NULL,
        date TEXT NOT NULL
    )
    """)

    # Fill products
    cursor.execute("DELETE FROM products")
    cursor.executemany(
        "INSERT INTO products (name, price) VALUES (?, ?)",
        [
            ("Café", 10),
            ("Thé", 8),
            ("Jus d'orange", 12),
            ("Cappuccino", 14),
            ("Eau Minérale", 5),
        ]
    )

    conn.commit()
    conn.close()
    print("Base de données créée avec succès !")

if __name__ == "__main__":
    init_db()
