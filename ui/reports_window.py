from typing import Any, Dict, Optional

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QMessageBox,
    QDateEdit,
)

from models import get_orders_between_dates, get_order_items


class ReportsWindow(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:  # type: ignore[name-defined]
        super().__init__(parent)
        self.setWindowTitle("Rapports des ventes")
        self.resize(800, 500)

        main_layout = QVBoxLayout()

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Date début :"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.start_date)

        filter_layout.addWidget(QLabel("Date fin :"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.end_date)

        self.filter_button = QPushButton("Afficher")
        self.filter_button.clicked.connect(self.load_orders)
        filter_layout.addWidget(self.filter_button)

        main_layout.addLayout(filter_layout)

        center_layout = QHBoxLayout()

        orders_group = QGroupBox("Commandes")
        orders_layout = QVBoxLayout()
        self.orders_list = QListWidget()
        self.orders_list.currentItemChanged.connect(self.on_order_selected)
        orders_layout.addWidget(self.orders_list)
        orders_group.setLayout(orders_layout)
        center_layout.addWidget(orders_group, 2)

        items_group = QGroupBox("Détails de la commande")
        items_layout = QVBoxLayout()
        self.items_list = QListWidget()
        items_layout.addWidget(self.items_list)
        items_group.setLayout(items_layout)
        center_layout.addWidget(items_group, 3)

        main_layout.addLayout(center_layout)

        self.total_label = QLabel("Total pour la période : 0.00 DH")
        main_layout.addWidget(self.total_label)

        self.setLayout(main_layout)

    def load_orders(self) -> None:
        self.orders_list.clear()
        self.items_list.clear()
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        orders = get_orders_between_dates(start, end)
        if not orders:
            QMessageBox.information(
                self,
                "Information",
                "Aucune commande pour cette période.",
            )
            self.total_label.setText("Total pour la période : 0.00 DH")
            return
        total_period = 0.0
        for o in orders:
            total_period += o["total"]
            text = (
                f"{o['date']} - {o['serveur']} - {o['total']:.2f} DH "
                f"(Cmd #{o['id']})"
            )
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, o)
            self.orders_list.addItem(item)
        self.total_label.setText(
            f"Total pour la période : {total_period:.2f} DH",
        )

    def on_order_selected(
        self,
        current: Optional[QListWidgetItem],  # type: ignore[valid-type]
        previous: Optional[QListWidgetItem],  # type: ignore[valid-type]
    ) -> None:
        self.items_list.clear()
        if not current:
            return
        order = current.data(Qt.UserRole)
        order_id = order["id"]
        items = get_order_items(order_id)
        for it in items:
            text = f"{it['name']} x{it['qty']} - {it['total']:.2f} DH"
            self.items_list.addItem(text)
