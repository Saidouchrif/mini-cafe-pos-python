from typing import Any, Dict, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)

from models import get_all_servers, create_server, update_server, delete_server


class ServersWindow(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:  # type: ignore[name-defined]
        super().__init__(parent)
        self.setWindowTitle("Gérer les serveurs")
        self.resize(500, 350)

        self.selected_user: Optional[Dict[str, Any]] = None

        main_layout = QVBoxLayout()

        list_group = QGroupBox("Serveurs")
        list_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        list_layout.addWidget(self.list_widget)
        list_group.setLayout(list_layout)
        main_layout.addWidget(list_group)

        form_group = QGroupBox("Détails du serveur")
        form_layout = QVBoxLayout()

        form_layout.addWidget(QLabel("Nom d'utilisateur :"))
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Nom d'utilisateur")
        form_layout.addWidget(self.username_edit)

        form_layout.addWidget(QLabel("Mot de passe :"))
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Mot de passe")
        self.password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.password_edit)

        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Ajouter")
        self.update_button = QPushButton("Modifier")
        self.delete_button = QPushButton("Supprimer")
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.update_button)
        buttons_layout.addWidget(self.delete_button)
        form_layout.addLayout(buttons_layout)

        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)

        self.setLayout(main_layout)

        self.list_widget.currentItemChanged.connect(self.on_selection_changed)
        self.add_button.clicked.connect(self.on_add)
        self.update_button.clicked.connect(self.on_update)
        self.delete_button.clicked.connect(self.on_delete)

        self.load_servers()

    def load_servers(self) -> None:
        self.list_widget.clear()
        servers = get_all_servers(include_admin=True)
        for s in servers:
            text = f"{s['username']} ({s['role']})"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, s)
            self.list_widget.addItem(item)

    def on_selection_changed(
        self,
        current: Optional[QListWidgetItem],  # type: ignore[valid-type]
        previous: Optional[QListWidgetItem],  # type: ignore[valid-type]
    ) -> None:
        if current is None:
            self.selected_user = None
            self.username_edit.clear()
            self.password_edit.clear()
            return
        user = current.data(Qt.UserRole)
        self.selected_user = user
        self.username_edit.setText(user["username"])
        self.password_edit.clear()

    def on_add(self) -> None:
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        if not username or not password:
            QMessageBox.warning(
                self,
                "Erreur",
                "Veuillez saisir un nom d'utilisateur et un mot de passe.",
            )
            return
        create_server(username, password, role="serveur")
        QMessageBox.information(self, "Succès", "Serveur ajouté.")
        self.username_edit.clear()
        self.password_edit.clear()
        self.load_servers()

    def on_update(self) -> None:
        if not self.selected_user:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un serveur.")
            return
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        if not username or not password:
            QMessageBox.warning(
                self,
                "Erreur",
                "Veuillez saisir un nom d'utilisateur et un mot de passe.",
            )
            return
        update_server(self.selected_user["id"], username, password)
        QMessageBox.information(self, "Succès", "Serveur modifié.")
        self.load_servers()

    def on_delete(self) -> None:
        if not self.selected_user:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un serveur.")
            return
        user_role = self.selected_user.get("role")
        if user_role == "admin":
            QMessageBox.warning(
                self,
                "Attention",
                "Impossible de supprimer le compte administrateur.",
            )
            return
        ok = delete_server(self.selected_user["id"])
        if not ok:
            QMessageBox.warning(self, "Erreur", "Impossible de supprimer cet utilisateur.")
            return
        QMessageBox.information(self, "Succès", "Serveur supprimé.")
        self.selected_user = None
        self.username_edit.clear()
        self.password_edit.clear()
        self.load_servers()
