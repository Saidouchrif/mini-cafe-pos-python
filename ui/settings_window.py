from typing import Optional

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)

from models import get_cafe_name, update_cafe_name


class SettingsWindow(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:  # type: ignore[name-defined]
        super().__init__(parent)
        self.setWindowTitle("Paramètres")
        self.resize(400, 180)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Nom du café :"))
        self.name_edit = QLineEdit()
        self.name_edit.setText(get_cafe_name())
        layout.addWidget(self.name_edit)

        self.save_button = QPushButton("Enregistrer")
        self.save_button.clicked.connect(self.on_save)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def on_save(self) -> None:
        new_name = self.name_edit.text().strip()
        if not new_name:
            QMessageBox.warning(
                self,
                "Erreur",
                "Le nom du café ne peut pas être vide.",
            )
            return
        update_cafe_name(new_name)
        QMessageBox.information(
            self,
            "Succès",
            "Nom du café mis à jour.",
        )
