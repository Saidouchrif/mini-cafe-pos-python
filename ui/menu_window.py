from typing import Any, Dict, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QMessageBox,
    QInputDialog,
)

from models import (
    get_categories,
    create_category,
    update_category,
    delete_category,
    get_products_by_category,
    create_product,
    update_product,
    delete_product,
)


class MenuWindow(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:  # type: ignore[name-defined]
        super().__init__(parent)
        self.setWindowTitle("Gérer le menu")
        self.resize(700, 400)

        self.selected_category_id: Optional[int] = None
        self.selected_product: Optional[Dict[str, Any]] = None

        main_layout = QHBoxLayout()

        cat_group = QGroupBox("Catégories")
        cat_layout = QVBoxLayout()
        self.categories_list = QListWidget()
        cat_layout.addWidget(self.categories_list)

        cat_buttons_layout = QHBoxLayout()
        self.add_cat_button = QPushButton("Ajouter")
        self.rename_cat_button = QPushButton("Renommer")
        self.delete_cat_button = QPushButton("Supprimer")
        cat_buttons_layout.addWidget(self.add_cat_button)
        cat_buttons_layout.addWidget(self.rename_cat_button)
        cat_buttons_layout.addWidget(self.delete_cat_button)
        cat_layout.addLayout(cat_buttons_layout)

        cat_group.setLayout(cat_layout)
        main_layout.addWidget(cat_group, 1)

        prod_group = QGroupBox("Produits")
        prod_layout = QVBoxLayout()
        prod_layout.addWidget(QLabel("Produits de la catégorie sélectionnée :"))
        self.products_list = QListWidget()
        prod_layout.addWidget(self.products_list)

        prod_buttons_layout = QHBoxLayout()
        self.add_prod_button = QPushButton("Ajouter")
        self.edit_prod_button = QPushButton("Modifier")
        self.delete_prod_button = QPushButton("Supprimer")
        prod_buttons_layout.addWidget(self.add_prod_button)
        prod_buttons_layout.addWidget(self.edit_prod_button)
        prod_buttons_layout.addWidget(self.delete_prod_button)
        prod_layout.addLayout(prod_buttons_layout)

        prod_group.setLayout(prod_layout)
        main_layout.addWidget(prod_group, 2)

        self.setLayout(main_layout)

        self.categories_list.currentItemChanged.connect(self.on_category_selected)
        self.products_list.currentItemChanged.connect(self.on_product_selected)
        self.add_cat_button.clicked.connect(self.on_add_category)
        self.rename_cat_button.clicked.connect(self.on_rename_category)
        self.delete_cat_button.clicked.connect(self.on_delete_category)
        self.add_prod_button.clicked.connect(self.on_add_product)
        self.edit_prod_button.clicked.connect(self.on_edit_product)
        self.delete_prod_button.clicked.connect(self.on_delete_product)

        self.load_categories()

    def load_categories(self) -> None:
        self.categories_list.clear()
        self.selected_category_id = None
        cats = get_categories()
        for c in cats:
            item = QListWidgetItem(c["name"])
            item.setData(Qt.UserRole, c)
            self.categories_list.addItem(item)

    def on_category_selected(
        self,
        current: Optional[QListWidgetItem],  # type: ignore[valid-type]
        previous: Optional[QListWidgetItem],  # type: ignore[valid-type]
    ) -> None:
        if not current:
            self.selected_category_id = None
            self.products_list.clear()
            return
        data = current.data(Qt.UserRole)
        self.selected_category_id = data["id"]
        self.load_products()

    def load_products(self) -> None:
        self.products_list.clear()
        self.selected_product = None
        if self.selected_category_id is None:
            return
        products = get_products_by_category(self.selected_category_id)
        for p in products:
            text = f"{p['name']} - {p['price']:.2f} DH"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, p)
            self.products_list.addItem(item)

    def on_product_selected(
        self,
        current: Optional[QListWidgetItem],  # type: ignore[valid-type]
        previous: Optional[QListWidgetItem],  # type: ignore[valid-type]
    ) -> None:
        if not current:
            self.selected_product = None
            return
        self.selected_product = current.data(Qt.UserRole)

    def on_add_category(self) -> None:
        name, ok = QInputDialog.getText(
            self,
            "Nouvelle catégorie",
            "Nom de la catégorie :",
        )
        if not ok:
            return
        name = name.strip()
        if not name:
            QMessageBox.warning(
                self,
                "Erreur",
                "Le nom de la catégorie est obligatoire.",
            )
            return
        create_category(name)
        self.load_categories()

    def on_rename_category(self) -> None:
        if self.selected_category_id is None:
            QMessageBox.warning(
                self,
                "Erreur",
                "Veuillez sélectionner une catégorie.",
            )
            return
        current_item = self.categories_list.currentItem()
        if current_item is None:
            return
        data = current_item.data(Qt.UserRole)
        current_name = data["name"]
        new_name, ok = QInputDialog.getText(
            self,
            "Renommer la catégorie",
            "Nouveau nom :",
            text=current_name,
        )
        if not ok:
            return
        new_name = new_name.strip()
        if not new_name:
            QMessageBox.warning(
                self,
                "Erreur",
                "Le nom de la catégorie est obligatoire.",
            )
            return
        update_category(self.selected_category_id, new_name)
        self.load_categories()

    def on_delete_category(self) -> None:
        if self.selected_category_id is None:
            QMessageBox.warning(
                self,
                "Erreur",
                "Veuillez sélectionner une catégorie.",
            )
            return
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Supprimer cette catégorie ?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        ok = delete_category(self.selected_category_id)
        if not ok:
            QMessageBox.warning(
                self,
                "Erreur",
                "Impossible de supprimer cette catégorie car elle contient des produits.",
            )
            return
        self.load_categories()
        self.products_list.clear()

    def on_add_product(self) -> None:
        if self.selected_category_id is None:
            QMessageBox.warning(
                self,
                "Erreur",
                "Veuillez sélectionner une catégorie.",
            )
            return
        name, ok = QInputDialog.getText(
            self,
            "Nouveau produit",
            "Nom du produit :",
        )
        if not ok:
            return
        name = name.strip()
        if not name:
            QMessageBox.warning(
                self,
                "Erreur",
                "Le nom du produit est obligatoire.",
            )
            return
        price_text, ok = QInputDialog.getText(
            self,
            "Nouveau produit",
            "Prix (en DH) :",
        )
        if not ok:
            return
        try:
            price = float(price_text.replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Prix invalide.")
            return
        create_product(name, price, self.selected_category_id)
        self.load_products()

    def on_edit_product(self) -> None:
        if not self.selected_product:
            QMessageBox.warning(
                self,
                "Erreur",
                "Veuillez sélectionner un produit.",
            )
            return
        name, ok = QInputDialog.getText(
            self,
            "Modifier le produit",
            "Nom du produit :",
            text=self.selected_product["name"],
        )
        if not ok:
            return
        name = name.strip()
        if not name:
            QMessageBox.warning(
                self,
                "Erreur",
                "Le nom du produit est obligatoire.",
            )
            return
        price_text, ok = QInputDialog.getText(
            self,
            "Modifier le produit",
            "Prix (en DH) :",
            text=f"{self.selected_product['price']:.2f}",
        )
        if not ok:
            return
        try:
            price = float(price_text.replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Prix invalide.")
            return
        update_product(self.selected_product["id"], name, price, self.selected_category_id)  # type: ignore[arg-type]
        self.load_products()

    def on_delete_product(self) -> None:
        if not self.selected_product:
            QMessageBox.warning(
                self,
                "Erreur",
                "Veuillez sélectionner un produit.",
            )
            return
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Supprimer ce produit ?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        delete_product(self.selected_product["id"])  # type: ignore[arg-type]
        self.load_products()
