from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QListWidget, QLabel, QMessageBox, QHBoxLayout, QVBoxLayout, QGroupBox
import sys

from menu import Menu
from products import ProductButtons
from database import get_conn

class MiniPOS(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Caisse Café - Mini Projet avec Images")
        self.resize(800, 500)

        self.total = 0.0

        main_layout = QHBoxLayout()

        # ================= MENU ==================
        menu_widget = Menu()
        main_layout.addWidget(menu_widget)

        # ================= CONTENT ================
        content_layout = QVBoxLayout()

        # PRODUITS AVEC IMAGES
        products_box = QGroupBox("Produits")
        pb = ProductButtons(self.add_to_cart)
        products_box.setLayout(pb.layout())
        content_layout.addWidget(products_box)

        # PANIER
        self.cart_list = QListWidget()
        content_layout.addWidget(QLabel("Panier :"))
        content_layout.addWidget(self.cart_list)

        # TOTAL + PAY
        bottom = QHBoxLayout()
        self.total_label = QLabel("Total : 0 DH")
        bottom.addWidget(self.total_label)

        btn_pay = QtWidgets.QPushButton("Paiement")
        btn_pay.clicked.connect(self.pay)
        bottom.addWidget(btn_pay)

        content_layout.addLayout(bottom)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def add_to_cart(self, name, price):
        self.cart_list.addItem(f"{name} - {price} DH")
        self.total += price
        self.total_label.setText(f"Total : {self.total} DH")

    def pay(self):
        if self.total <= 0:
            QMessageBox.warning(self, "Erreur", "Le panier est vide.")
            return

        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sales (total, date) VALUES (?, datetime('now'))",
            (self.total,)
        )
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Succès", f"Paiement effectué : {self.total} DH")

        # Reset cart
        self.cart_list.clear()
        self.total = 0
        self.total_label.setText("Total : 0 DH")


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MiniPOS()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
