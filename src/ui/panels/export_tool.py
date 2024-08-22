import logging
import os
import platform
import subprocess
from datetime import datetime

from panda3d.core import AntialiasAttrib
from platformdirs import user_pictures_dir
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QIntValidator
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)

DEFAULT_ANTI_ALIASING_LEVEL = 0
ANTI_ALIASING_OPTIONS = ["None", "4", "8", "16"]
STANDARD_SIZES_WIDTH = ["1280", "1920", "2560", "3840", "7680"]
STANDARD_SIZES_HEIGHT = ["720", "1080", "1440", "2160", "4320"]
FRAME_DELAY_MS = 1000


class ImageExportWidget(QWidget):
    def __init__(self, viewport_widget, status_bar, parent=None):
        super().__init__(parent)
        self.viewport_widget = viewport_widget
        self.status_bar = status_bar
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface for the image export widget."""
        self.setWindowTitle("Export Tool")

        form_layout = self._create_form_layout()
        main_layout = self._create_main_layout(form_layout)

        container_widget = QWidget()
        container_widget.setLayout(main_layout)

        scroll_area = QScrollArea()
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container_widget)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll_area)
        self.setLayout(outer_layout)

    def _create_form_layout(self):
        """Create the form layout with user input fields."""
        form_layout = QFormLayout()

        self.width_input = self._create_size_input(STANDARD_SIZES_WIDTH)
        self.height_input = self._create_size_input(STANDARD_SIZES_HEIGHT)
        self.anti_aliasing_input = self._create_anti_aliasing_input()
        self.save_path_input = self._create_save_path_input()
        self.preview_checkbox = self._create_preview_checkbox()

        form_layout.addRow("Width:", self.width_input)
        form_layout.addRow("Height:", self.height_input)
        form_layout.addRow("Anti-Aliasing:", self.anti_aliasing_input)
        form_layout.addRow("Export Path:", self.save_path_input)
        form_layout.addRow(self.preview_checkbox)

        return form_layout

    def _create_main_layout(self, form_layout):
        """Create the main layout with form layout and control buttons."""
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self._create_browse_button())
        main_layout.addWidget(self._create_save_button())
        main_layout.addStretch()
        return main_layout

    def _create_size_input(self, standard_sizes):
        """Create a QComboBox with standard sizes and allow custom input."""
        size_input = QComboBox(self)
        size_input.addItems(standard_sizes)
        size_input.setEditable(True)
        size_input.lineEdit().setValidator(QIntValidator())
        return size_input

    def _create_anti_aliasing_input(self):
        """Create a QComboBox for anti-aliasing level selection with predefined values."""
        anti_aliasing_input = QComboBox(self)
        anti_aliasing_input.addItems(ANTI_ALIASING_OPTIONS)
        anti_aliasing_input.setCurrentIndex(ANTI_ALIASING_OPTIONS.index("None"))
        anti_aliasing_input.currentIndexChanged.connect(self._update_aliasing_level)
        anti_aliasing_input.setFocusPolicy(Qt.NoFocus)
        self.aliasing_level = DEFAULT_ANTI_ALIASING_LEVEL
        return anti_aliasing_input

    def _create_save_path_input(self):
        """Create a QLineEdit for displaying the selected save path."""
        save_path_input = QLineEdit(self)
        save_path_input.setText(user_pictures_dir())
        return save_path_input

    def _create_preview_checkbox(self):
        """Create a QCheckBox for enabling/disabling image preview after export."""
        preview_checkbox = QCheckBox("Show Preview After Export", self)
        preview_checkbox.setChecked(True)
        return preview_checkbox

    def _create_browse_button(self):
        """Create a button for browsing export folder."""
        browse_button = QPushButton(QIcon.fromTheme("folder"), "Browse...")
        browse_button.clicked.connect(self._select_export_folder)
        browse_button.setFixedHeight(50)
        return browse_button

    def _create_save_button(self):
        """Create a button for saving the exported image."""
        save_button = QPushButton(QIcon.fromTheme("camera-photo"), "Export")
        save_button.clicked.connect(self._export_image)
        save_button.setFixedHeight(50)
        return save_button

    def _update_aliasing_level(self):
        """Update the anti-aliasing level based on user selection."""
        _current_value = self.anti_aliasing_input.currentText()
        if _current_value == "None":
            self.aliasing_level = 0
        else:
            self.aliasing_level = int(_current_value)

    def _select_export_folder(self):
        """Open a dialog to select the folder where the image will be saved."""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.save_path_input.setText(folder_path)

    def _generate_save_path(self, folder_path):
        """Generate a full save path with a timestamped filename."""
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"image-{timestamp}.png"
        return os.path.join(folder_path, filename)

    def _export_image(self):
        """Validate inputs, resize the viewport, and request the image to be captured."""
        width, height, folder_path = self._get_user_inputs()
        if not width or not height or not folder_path:
            QMessageBox.warning(
                self,
                "Input Error",
                "Please enter valid width, height, and choose a path to save the image.",
            )
            return

        self.save_path = self._generate_save_path(folder_path)
        self._prepare_for_export(width, height)
        self._capture_next_frame()

    def _prepare_for_export(self, width, height):
        """Prepare the viewport and settings for exporting the image."""
        self.old_size = self.viewport_widget.size()
        self.requested_width = width
        self.requested_height = height
        self.should_show_preview = self.preview_checkbox.isChecked()

        if self.aliasing_level != DEFAULT_ANTI_ALIASING_LEVEL:
            self.viewport_widget.engine.render.setAntialias(
                AntialiasAttrib.MMultisample, self.aliasing_level
            )

        self.viewport_widget.engine.scene_manager.hide_grid()

        self.viewport_widget.size_changed.emit(width, height)

    def _capture_next_frame(self):
        """Capture the next frame after a short delay to ensure resizing is complete."""
        QTimer.singleShot(
            FRAME_DELAY_MS / self.viewport_widget.engine.fps_cap,
            self._capture_and_save_image,
        )

    def _capture_and_save_image(self):
        """Capture the current frame as an image and save it to the specified path."""
        image = self.viewport_widget.pixmap.toImage()

        if not image.isNull() and self._is_image_size_correct(image):
            self._save_image(image)
        else:
            logger.warning(
                "Captured image is either null or doesn't match the requested size, waiting for the next frame..."
            )
            QTimer.singleShot(
                FRAME_DELAY_MS / self.viewport_widget.engine.fps_cap,
                self._capture_and_save_image,
            )

    def _is_image_size_correct(self, image):
        """Check if the captured image size matches the requested size."""
        return (
            image.width() == self.requested_width
            and image.height() == self.requested_height
        )

    def _save_image(self, image):
        """Save the captured image to the specified path and show a preview if enabled."""
        if image.save(self.save_path):
            logger.info("Image saved successfully to %s", self.save_path)
            self.status_bar.showMessage(
                f"Image saved successfully to {self.save_path}", 5000
            )
            self._show_preview()
        else:
            QMessageBox.critical(self, "Save Error", "Failed to save the image.")
            logger.error("Failed to save the image.")

        self._restore_viewport_settings()

    def _show_preview(self):
        """Display the image preview if the corresponding option is checked."""
        if self.should_show_preview:
            self._open_photo(self.save_path)

    def _restore_viewport_settings(self):
        """Restore the viewport size and engine state after the image export."""
        self.viewport_widget.size_changed.emit(
            self.old_size.width(), self.old_size.height()
        )
        self.viewport_widget.engine.render.setAntialias(AntialiasAttrib.MNone)
        self.viewport_widget.engine.scene_manager.show_grid()

    def _get_user_inputs(self):
        """Retrieve and validate user inputs for width, height, and save path."""
        width = self._get_combobox_value(self.width_input)
        height = self._get_combobox_value(self.height_input)

        if width is None or height is None:
            QMessageBox.warning(
                self,
                "Input Error",
                "Width and height must be integers.",
            )
            return None, None, None

        folder_path = self.save_path_input.text()
        return width, height, folder_path

    def _get_combobox_value(self, combobox):
        """Retrieve the value from a QComboBox and validate it."""
        text = combobox.currentText()
        return int(text) if text.isdigit() else None

    @staticmethod
    def _open_photo(file_path):
        """Open the photo using the system's default image viewer."""
        system = platform.system()

        if system == "Windows":
            os.startfile(file_path)
        elif system == "Darwin":
            subprocess.run(["open", file_path])
        else:
            subprocess.run(["xdg-open", file_path])
