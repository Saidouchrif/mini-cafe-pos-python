# app.py
import sys
import os
from datetime import datetime

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QMessageBox, QListWidget,
    QListWidgetItem
)
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

from database import init_db, get_conn, DB_NAME


# ==========================
# Fenêtre de Login Serveur
# ==========================
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connexion Serveur")
        self.resize(300, 150)

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur (serveur)")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.login_btn = QPushButton("Se connecter")
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")
            return

        conn = get_conn()
        c = conn.cursor()
        c.execute(
            "SELECT id, role FROM users WHERE username=? AND password=?",
            (username, password)
        )
        row = c.fetchone()
        conn.close()

        if row:
            user_id, role = row
            # ouvrir la fenêtre principale POS
            self.pos_window = POSWindow(user_id, username)
            self.pos_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Erreur", "Identifiants incorrects.")


# ==========================
# Fenêtre principale POS
# ==========================
class POSWindow(QWidget):
    def __init__(self, serveur_id, serveur_name):
        super().__init__()
        self.serveur_id = serveur_id
        self.serveur_name = serveur_name

        self.setWindowTitle(f"Caisse Café - Serveur: {serveur_name}")
        self.resize(1000, 600)

        # Cart structure: {product_id: {"name":..., "price":..., "qty":...}}
        self.cart = {}
        self.total = 0.0

        main_layout = QHBoxLayout()

        # ======== PARTIE GAUCHE : Catégories =========
        self.categories_box = QGroupBox("Catégories")
        cat_layout = QVBoxLayout()

        self.category_buttons = []
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id, name FROM categories")
        self.categories = c.fetchall()  # [(id, name), ...]
        conn.close()

        for cat_id, cat_name in self.categories:
            btn = QPushButton(cat_name)
            btn.setFixedHeight(40)
            btn.clicked.connect(
                lambda checked, cid=cat_id: self.load_products(cid)
            )
            cat_layout.addWidget(btn)
            self.category_buttons.append(btn)

        self.categories_box.setLayout(cat_layout)
        main_layout.addWidget(self.categories_box, 1)

        # ======== PARTIE CENTRE : Produits =========
        self.products_box = QGroupBox("Produits")
        self.products_layout = QVBoxLayout()
        self.products_box.setLayout(self.products_layout)
        main_layout.addWidget(self.products_box, 2)

        # ======== PARTIE DROITE : Commande (Panier) =========
        right_layout = QVBoxLayout()

        self.cart_list = QListWidget()
        right_layout.addWidget(QLabel("Commande en cours :"))
        right_layout.addWidget(self.cart_list)

        # Total + Paiement
        bottom_layout = QHBoxLayout()
        self.total_label = QLabel("Total : 0.00 DH")
        bottom_layout.addWidget(self.total_label)

        self.pay_btn = QPushButton("Paiement")
        self.pay_btn.clicked.connect(self.handle_payment)
        bottom_layout.addWidget(self.pay_btn)

        right_layout.addLayout(bottom_layout)

        right_box = QGroupBox("Détails")
        right_box.setLayout(right_layout)
        main_layout.addWidget(right_box, 2)

        self.setLayout(main_layout)

        # Charger par défaut la première catégorie
        if self.categories:
            first_cat_id, _ = self.categories[0]
            self.load_products(first_cat_id)

    # ================= CHARGER PRODUITS PAR CAT =================
    def load_products(self, category_id):
        # vider layout produits
        for i in reversed(range(self.products_layout.count())):
            w = self.products_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        conn = get_conn()
        c = conn.cursor()
        c.execute(
            "SELECT id, name, price FROM products WHERE category_id=?",
            (category_id,)
        )
        products = c.fetchall()
        conn.close()

        if not products:
            self.products_layout.addWidget(QLabel("Aucun produit dans cette catégorie."))
            return

        for prod_id, name, price in products:
            btn = QPushButton(f"{name} - {price:.2f} DH")
            btn.setFixedHeight(40)
            btn.clicked.connect(
                lambda checked, pid=prod_id, n=name, p=price: self.add_to_cart(pid, n, p)
            )
            self.products_layout.addWidget(btn)

    # ================= GESTION DU PANIER =================
    def add_to_cart(self, product_id, name, price):
        """Ajouter ou incrémenter un produit dans la commande."""
        if product_id in self.cart:
            self.cart[product_id]["qty"] += 1
        else:
            self.cart[product_id] = {
                "name": name,
                "price": price,
                "qty": 1
            }
        self.refresh_cart()

    def remove_from_cart(self, product_id):
        """Annuler un produit de la commande."""
        if product_id in self.cart:
            del self.cart[product_id]
            self.refresh_cart()

    def refresh_cart(self):
        self.cart_list.clear()
        self.total = 0.0

        for prod_id, data in self.cart.items():
            name = data["name"]
            price = data["price"]
            qty = data["qty"]
            line_total = price * qty
            self.total += line_total

            item = QListWidgetItem()
            row_widget = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)

            label = QLabel(f"{name} x{qty} - {line_total:.2f} DH")
            btn_cancel = QPushButton("Annuler")
            btn_cancel.setFixedWidth(80)
            btn_cancel.clicked.connect(
                lambda checked, pid=prod_id: self.remove_from_cart(pid)
            )

            row_layout.addWidget(label)
            row_layout.addWidget(btn_cancel)
            row_widget.setLayout(row_layout)

            self.cart_list.addItem(item)
            self.cart_list.setItemWidget(item, row_widget)

        self.total_label.setText(f"Total : {self.total:.2f} DH")

    # ======================= PAIEMENT =======================
    def handle_payment(self):
        if not self.cart:
            QMessageBox.warning(self, "Erreur", "La commande est vide.")
            return

        conn = get_conn()
        c = conn.cursor()

        # Insérer la commande
        c.execute(
            "INSERT INTO orders (serveur_id, total, date) VALUES (?, ?, ?)",
            (self.serveur_id, self.total, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        order_id = c.lastrowid

        # Insérer les lignes de commande
        for prod_id, data in self.cart.items():
            c.execute(
                "INSERT INTO order_items (order_id, product_id, qty, price) VALUES (?, ?, ?, ?)",
                (order_id, prod_id, data["qty"], data["price"])
            )

        conn.commit()
        conn.close()

        # Générer et imprimer ticket
        self.generate_and_print_ticket(order_id)

        QMessageBox.information(self, "Succès", "Paiement effectué et ticket généré.")
        self.cart = {}
        self.refresh_cart()

    # =================== TICKET EN FRANÇAIS ===================
    def generate_and_print_ticket(self, order_id):
        """Génère un ticket en français et tente de l'envoyer à l'imprimante."""
        # Charger données commande
        conn = get_conn()
        c = conn.cursor()

        c.execute("""
            SELECT o.id, o.total, o.date, u.username
            FROM orders o
            JOIN users u ON o.serveur_id = u.id
            WHERE o.id=?
        """, (order_id,))
        order = c.fetchone()

        c.execute("""
            SELECT p.name, oi.qty, oi.price
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id=?
        """, (order_id,))
        items = c.fetchall()

        conn.close()

        if not order:
            return

        order_id, total, date_str, serveur_name = order

        lines = []
        lines.append("        Café Ouchrif")
        lines.append("   Ticket de caisse officiel")
        lines.append("--------------------------------")
        lines.append(f"Serveur : {serveur_name}")
        lines.append(f"Date    : {date_str}")
        lines.append(f"N° Cmd  : {order_id}")
        lines.append("--------------------------------")

        for name, qty, price in items:
            line_total = qty * price
            lines.append(f"{name} x{qty}  {line_total:.2f} DH")

        lines.append("--------------------------------")
        lines.append(f"TOTAL A PAYER : {total:.2f} DH")
        lines.append("--------------------------------")
        lines.append("Merci pour votre visite !")
        lines.append("À très bientôt.")
        lines.append("")

        ticket_text = "\n".join(lines)

        # حفظ التذكرة فـ fichier
        ticket_name = f"ticket_{order_id}.txt"
        with open(ticket_name, "w", encoding="utf-8") as f:
            f.write(ticket_text)

        # محاولة طباعة التذكرة (Windows)
        try:
            os.startfile(ticket_name, "print")  # يرسلها للـ imprimante par défaut
        except Exception as e:
            # الى ما قدرش يطبع -> نقولو ليه يطبعها يدوي
            QMessageBox.information(
                self,
                "Ticket généré",
                f"Ticket enregistré dans : {os.path.abspath(ticket_name)}\n"
                "Vous pouvez l'imprimer manuellement."
            )


# ==================== MAIN ====================
def main():
    # créer la base automatiquement si elle n'existe pas
    init_db()

    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
