import sys
import sqlite3
from pathlib import Path
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QListWidget, QLabel, QMessageBox,
    QHBoxLayout, QVBoxLayout, QGroupBox, QListWidgetItem
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

DB_NAME = "cafe.db"


# =========================================================
# =============== DATABASE AUTO CREATION ===================
# =========================================================
def init_database():
    """Create the database and tables if they do not exist."""
    db_path = Path(DB_NAME)
    create_new = not db_path.exists()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        total REAL NOT NULL,
        date TEXT NOT NULL
    )
    """)

    # Insert sample products if DB was new
    if create_new:
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


# =========================================================
# ==================== MAIN UI CLASS ======================
# =========================================================
class MiniPOS(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Caisse Café")
        self.resize(800, 500)

        self.cart = {}  # {product_name: [price, qty]}
        self.total = 0.0

        main_layout = QHBoxLayout()

        # ================= MENU ==================
        menu = QVBoxLayout()

        for icon_name in ["menu_home", "menu_products", "menu_caisse", "menu_settings"]:
            btn = QPushButton()
            btn.setIcon(QIcon(f"assets/{icon_name}.png"))
            btn.setIconSize(QSize(40, 40))
            menu.addWidget(btn)

        menu_box = QGroupBox("Menu")
        menu_box.setLayout(menu)
        main_layout.addWidget(menu_box)

        # ================= CONTENT ==================
        content_layout = QVBoxLayout()

        # Products UI
        products_box = QGroupBox("Produits")
        products_layout = QVBoxLayout()

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT name, price FROM products")
        products = cursor.fetchall()
        conn.close()

        for name, price in products:
            btn = QPushButton(f"{name} - {price} DH")
            btn.clicked.connect(lambda checked, n=name, p=price: self.add_to_cart(n, p))
            products_layout.addWidget(btn)

        products_box.setLayout(products_layout)
        content_layout.addWidget(products_box)

        # Panier
        self.cart_list = QListWidget()
        content_layout.addWidget(QLabel("Panier :"))
        content_layout.addWidget(self.cart_list)

        # Total + Pay
        bottom = QHBoxLayout()
        self.total_label = QLabel("Total : 0 DH")
        bottom.addWidget(self.total_label)

        btn_pay = QPushButton("Paiement")
        btn_pay.clicked.connect(self.pay)
        bottom.addWidget(btn_pay)

        content_layout.addLayout(bottom)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    # ======================================================
    # ================== CART SYSTEM =======================
    # ======================================================
    def add_to_cart(self, name, price):
        """Add product or increase quantity"""
        if name in self.cart:
            self.cart[name][1] += 1
        else:
            self.cart[name] = [price, 1]

        self.refresh_cart()

    def remove_item(self, item_name):
        """Remove one quantity"""
        if self.cart[item_name][1] > 1:
            self.cart[item_name][1] -= 1
        else:
            del self.cart[item_name]
        self.refresh_cart()

    def refresh_cart(self):
        """Refresh the display of cart"""
        self.cart_list.clear()
        self.total = 0

        for name, (price, qty) in self.cart.items():
            total_line = price * qty
            self.total += total_line

            item = QListWidgetItem(f"{name} - {price} DH x{qty}")
            self.cart_list.addItem(item)

            # Button X on each line
            btn = QPushButton("❌")
            btn.clicked.connect(lambda checked, n=name: self.remove_item(n))
            self.cart_list.setItemWidget(item, btn)

        self.total_label.setText(f"Total : {self.total} DH")

    # ======================================================
    # ==================== PAYMENT ==========================
    # ======================================================
    def pay(self):
        if self.total <= 0:
            QMessageBox.warning(self, "Erreur", "Le panier est vide.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sales (total, date) VALUES (?, datetime('now'))",
            (self.total,)
        )
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Succès", f"Paiement effectué : {self.total} DH")

        # Clear cart
        self.cart = {}
        self.refresh_cart()


# =========================================================
# ===================== MAIN ==============================
# =========================================================
def main():
    init_database()  # AUTO database creation
    app = QtWidgets.QApplication(sys.argv)
    window = MiniPOS()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
