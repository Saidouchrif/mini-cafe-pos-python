from typing import Any, Dict

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
)

from utils.auth import is_admin
from ui.servers_window import ServersWindow
from ui.menu_window import MenuWindow
from ui.pos_window import POSWindow
from ui.reports_window import ReportsWindow
from ui.settings_window import SettingsWindow


class AdminDashboardWindow(QWidget):
    def __init__(self, user: Dict[str, Any]) -> None:
        super().__init__()
        self.user = user
        self.setWindowTitle("Café Caisse Manager - Tableau de bord administrateur")
        self.resize(400, 350)

        if not is_admin(self.user):
            QMessageBox.critical(
                self,
                "Accès refusé",
                "Cette fenêtre est réservée à l'administrateur.",
            )
            self.close()
            return

        layout = QVBoxLayout()

        label = QLabel(
            f"Connecté en tant qu'administrateur : {self.user.get('username', '')}"
        )
        layout.addWidget(label)

        self.servers_button = QPushButton("Gérer les serveurs")
        self.menu_button = QPushButton("Gérer le menu")
        self.pos_button = QPushButton("Ouvrir la caisse")
        self.reports_button = QPushButton("Rapports")
        self.settings_button = QPushButton("Paramètres")

        for btn in (
            self.servers_button,
            self.menu_button,
            self.pos_button,
            self.reports_button,
            self.settings_button,
        ):
            btn.setMinimumHeight(45)
            btn.setStyleSheet("font-size: 14px;")
            layout.addWidget(btn)

        self.servers_button.clicked.connect(self.open_servers)
        self.menu_button.clicked.connect(self.open_menu)
        self.pos_button.clicked.connect(self.open_pos)
        self.reports_button.clicked.connect(self.open_reports)
        self.settings_button.clicked.connect(self.open_settings)

        self.setLayout(layout)

    def open_servers(self) -> None:
        self.servers_window = ServersWindow(self)
        self.servers_window.show()

    def open_menu(self) -> None:
        self.menu_window = MenuWindow(self)
        self.menu_window.show()

    def open_pos(self) -> None:
        self.pos_window = POSWindow(self.user, parent=self)
        self.pos_window.show()

    def open_reports(self) -> None:
        self.reports_window = ReportsWindow(self)
        self.reports_window.show()

    def open_settings(self) -> None:
        self.settings_window = SettingsWindow(self)
        self.settings_window.show()
