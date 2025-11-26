from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

class Menu(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        btn_home = QPushButton()
        btn_home.setIcon(QIcon("assets/menu_home.png"))
        btn_home.setIconSize(QSize(40, 40))
        layout.addWidget(btn_home)

        btn_products = QPushButton()
        btn_products.setIcon(QIcon("assets/menu_products.png"))
        btn_products.setIconSize(QSize(40, 40))
        layout.addWidget(btn_products)

        btn_caisse = QPushButton()
        btn_caisse.setIcon(QIcon("assets/menu_caisse.png"))
        btn_caisse.setIconSize(QSize(40, 40))
        layout.addWidget(btn_caisse)

        btn_settings = QPushButton()
        btn_settings.setIcon(QIcon("assets/menu_settings.png"))
        btn_settings.setIconSize(QSize(40, 40))
        layout.addWidget(btn_settings)

        self.setLayout(layout)
