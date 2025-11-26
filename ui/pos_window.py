from typing import Any, Dict, Optional

from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QMessageBox,
)

from models import get_categories, get_products_by_category, create_order
from utils.tickets import generate_and_print_ticket


class POSWindow(QWidget):
    def __init__(self, user: Dict[str, Any], parent: Optional[QWidget] = None) -> None:  # type: ignore[name-defined]
        super().__init__(parent)
        self.user = user
        self.serveur_id = user["id"]
        self.serveur_name = user["username"]

        self.setWindowTitle(f"Caisse - {self.serveur_name}")
        self.resize(1000, 600)

        self.cart: Dict[int, Dict[str, Any]] = {}
        self.total = 0.0

        main_layout = QHBoxLayout()

        cat_group = QGroupBox("Catégories")
        cat_layout = QVBoxLayout()
        self.category_buttons = []
        self.categories = get_categories()
        for c in self.categories:
            btn = QPushButton(c["name"])
            btn.setFixedHeight(40)
            btn.clicked.connect(
                lambda checked, cid=c["id"]: self.load_products(cid)
            )
            cat_layout.addWidget(btn)
            self.category_buttons.append(btn)
        cat_group.setLayout(cat_layout)
        main_layout.addWidget(cat_group, 1)

        prod_group = QGroupBox("Produits")
        self.products_layout = QVBoxLayout()
        prod_group.setLayout(self.products_layout)
        main_layout.addWidget(prod_group, 2)

        right_group = QGroupBox("Commande")
        right_layout = QVBoxLayout()

        self.server_label = QLabel(f"Serveur connecté : {self.serveur_name}")
        right_layout.addWidget(self.server_label)

        right_layout.addWidget(QLabel("Commande en cours :"))
        self.cart_list = QListWidget()
        right_layout.addWidget(self.cart_list)

        bottom_layout = QHBoxLayout()
        self.total_label = QLabel("Total : 0.00 DH")
        bottom_layout.addWidget(self.total_label)

        self.pay_button = QPushButton("Paiement")
        self.pay_button.clicked.connect(self.handle_payment)
        bottom_layout.addWidget(self.pay_button)

        right_layout.addLayout(bottom_layout)
        right_group.setLayout(right_layout)
        main_layout.addWidget(right_group, 2)

        self.setLayout(main_layout)

        if self.categories:
            self.load_products(self.categories[0]["id"])

    def clear_products_layout(self) -> None:
        for i in reversed(range(self.products_layout.count())):
            item = self.products_layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def load_products(self, category_id: int) -> None:
        self.clear_products_layout()
        products = get_products_by_category(category_id)
        if not products:
            self.products_layout.addWidget(
                QLabel("Aucun produit dans cette catégorie."),
            )
            return
        for p in products:
            btn = QPushButton(f"{p['name']} - {p['price']:.2f} DH")
            btn.setFixedHeight(40)
            btn.clicked.connect(
                lambda checked, pid=p["id"], name=p["name"], price=p["price"]: self.add_to_cart(  # type: ignore[call-arg]
                    pid,
                    name,
                    price,
                )
            )
            self.products_layout.addWidget(btn)

    def add_to_cart(self, product_id: int, name: str, price: float) -> None:
        if product_id in self.cart:
            self.cart[product_id]["qty"] += 1
        else:
            self.cart[product_id] = {
                "name": name,
                "price": price,
                "qty": 1,
            }
        self.refresh_cart()

    def remove_from_cart(self, product_id: int) -> None:
        if product_id in self.cart:
            del self.cart[product_id]
            self.refresh_cart()

    def refresh_cart(self) -> None:
        self.cart_list.clear()
        self.total = 0.0
        for prod_id, item in self.cart.items():
            line_total = item["price"] * item["qty"]
            self.total += line_total

            list_item = QListWidgetItem()
            row_widget = QWidget()
            row_layout = QVBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)

            label = QLabel(
                f"{item['name']} x{item['qty']} - {line_total:.2f} DH",
            )
            cancel_button = QPushButton("Annuler")
            cancel_button.setFixedWidth(80)
            cancel_button.clicked.connect(
                lambda checked, pid=prod_id: self.remove_from_cart(pid)
            )

            row_layout.addWidget(label)
            row_layout.addWidget(cancel_button)
            row_widget.setLayout(row_layout)

            self.cart_list.addItem(list_item)
            self.cart_list.setItemWidget(list_item, row_widget)

        self.total_label.setText(f"Total : {self.total:.2f} DH")

    def handle_payment(self) -> None:
        if not self.cart:
            QMessageBox.warning(self, "Erreur", "La commande est vide.")
            return
        order_id = create_order(self.serveur_id, self.cart)
        generate_and_print_ticket(order_id, parent=self)
        QMessageBox.information(
            self,
            "Succès",
            "Paiement effectué et ticket généré.",
        )
        self.cart = {}
        self.refresh_cart()
