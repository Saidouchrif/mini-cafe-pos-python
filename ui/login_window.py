from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)

from models import authenticate_user
from utils.auth import is_admin
from ui.admin_dashboard import AdminDashboardWindow
from ui.pos_window import POSWindow


class LoginWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Café Caisse Manager - Connexion")
        self.resize(350, 180)

        layout = QVBoxLayout()

        title_label = QLabel("Connexion")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Se connecter")
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def handle_login(self) -> None:
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")
            return

        user = authenticate_user(username, password)
        if not user:
            QMessageBox.warning(self, "Erreur", "Identifiants incorrects.")
            return

        if is_admin(user):
            self.next_window = AdminDashboardWindow(user)
        else:
            self.next_window = POSWindow(user)

        self.next_window.show()
        self.close()
