from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

class ProductButtons(QWidget):
    def __init__(self, callback):
        super().__init__()

        self.callback = callback
        layout = QVBoxLayout()

        btn_cafe = QPushButton("Café - 10 DH")
        btn_cafe.setIcon(QIcon("assets/cafe.png"))
        btn_cafe.setIconSize(QSize(50, 50))
        btn_cafe.clicked.connect(lambda: self.callback("Café", 10))
        layout.addWidget(btn_cafe)

        btn_the = QPushButton("Thé - 8 DH")
        btn_the.setIcon(QIcon("assets/the.png"))
        btn_the.setIconSize(QSize(50, 50))
        btn_the.clicked.connect(lambda: self.callback("Thé", 8))
        layout.addWidget(btn_the)

        btn_jus = QPushButton("Jus - 12 DH")
        btn_jus.setIcon(QIcon("assets/jus.png"))
        btn_jus.setIconSize(QSize(50, 50))
        btn_jus.clicked.connect(lambda: self.callback("Jus d'orange", 12))
        layout.addWidget(btn_jus)

        self.setLayout(layout)
