import os
import sys

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)


class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("About PandaQt")
        self.setFixedSize(550, 350)

        icon_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ),
            "resources",
            "icon.png",
        )
        self.setWindowIcon(QPixmap(icon_path).scaled(128, 128))

        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(icon_path).scaled(128, 128))
        icon_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        header_label = QLabel("<h2>About PandaQt</h2>")

        description_label = QLabel(
            """
            <p>Welcome to PandaQt!</p>
            <p>This application demonstrates how to embed the Panda3D game engine into a PySide6/Qt application, allowing you to integrate Panda3D's powerful rendering capabilities directly within a standard QWidget.</p>
            <p>For more information and to access the source code, visit the project's <a href="https://github.com/killian-w/PandaQt">GitHub repository</a>.</p>
            """
        )
        description_label.setWordWrap(True)
        description_label.setOpenExternalLinks(True)

        license_label = QLabel("<h3>License</h3>")

        license_info_label = QLabel(
            "This project is licensed under the <a href='https://opensource.org/license/MIT'>MIT License</a>."
        )
        license_info_label.setOpenExternalLinks(True)

        copyright_label = QLabel("<h3>Copyright</h3>")

        copyright_info_label = QLabel(
            """
            <p>Copyright (c) 2024, Killian.</p>
            <b>All trademarks, including the Panda3D and Qt logos, are property of their respective owners.</b>
            """
        )
        copyright_info_label.setWordWrap(True)

        text_layout = QVBoxLayout()
        text_layout.addWidget(header_label)
        text_layout.addWidget(description_label)
        text_layout.addWidget(license_label)
        text_layout.addWidget(license_info_label)
        text_layout.addWidget(copyright_label)
        text_layout.addWidget(copyright_info_label)

        icon_layout = QVBoxLayout()
        icon_layout.addWidget(icon_label)
        icon_layout.addStretch()

        main_layout = QHBoxLayout()
        main_layout.addLayout(icon_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(text_layout)

        okay_button = QPushButton("Okay")
        okay_button.clicked.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(okay_button)

        final_layout = QVBoxLayout()
        final_layout.addLayout(main_layout)
        final_layout.addLayout(button_layout)

        self.setLayout(final_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AboutDialog()
    window.show()
    sys.exit(app.exec())
