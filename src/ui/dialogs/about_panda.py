import os
import sys

from panda3d.core import PandaSystem
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


class AboutPanda3DDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("About Panda3D")
        self.setFixedSize(550, 375)

        icon_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ),
            "resources",
            "panda3d_icon.png",
        )
        self.setWindowIcon(QPixmap(icon_path).scaled(128, 128))

        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(icon_path).scaled(128, 128))
        icon_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        header_label = QLabel("<h2>About Panda3D</h2>")

        description_label = QLabel(
            f"""
            <p>This program uses Panda3D version {PandaSystem.getVersionString()}.</p>
            <p>Panda3D is a versatile game engine and framework designed for 3D rendering and game development.</p>
            <p>It supports both Python and C++ programming, making it a flexible choice for developers.</p>
            <p>Panda3D is open-source and free to use for any purpose, including commercial applications, thanks to its permissive license.</p>
            <p>For more information and to access the source code, visit the
            <a href="https://github.com/panda3d/panda3d">Panda3D GitHub repository</a> or the
            <a href="https://www.panda3d.org">Panda3D website</a>.</p>
            """
        )
        description_label.setWordWrap(True)
        description_label.setOpenExternalLinks(True)

        license_label = QLabel("<h3>License</h3>")

        license_info_label = QLabel(
            "Panda3D is licensed under the <a href='https://opensource.org/license/BSD-2-Clause'>Modified BSD License</a>."
        )
        license_info_label.setOpenExternalLinks(True)

        copyright_label = QLabel("<h3>Copyright</h3>")

        copyright_info_label = QLabel("Copyright (c) 2008, Carnegie Mellon University.")

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
    window = AboutPanda3DDialog()
    window.show()
    sys.exit(app.exec())
