"""
Main application window for the Panda3D + PySide6 application.
"""

import logging

from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QStatusBar,
)

from engine.engine_widget import EngineWidget

from .dialogs.about import AboutDialog
from .dialogs.about_panda import AboutPanda3DDialog
from .dock_widgets import setup_docks

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Main window class for the Panda3D + PySide6 application.
    """

    def __init__(self, fps_cap):
        """
        Initialize the main window.
        """
        super().__init__()

        self.fps_cap = fps_cap
        self._init_ui()
        self._setup_menu()
        self._setup_status_bar()
        setup_docks(self)

        self.viewport_widget.size_changed.connect(self._update_resolution_label)
        self.viewport_widget.engine.notifier.fps_updated.connect(self._update_fps_label)

    def _init_ui(self):
        """
        Initialize the 3D viewport.
        """
        self.setMinimumSize(640, 360)
        self.setWindowTitle("PandaQt")

        self.viewport_widget = EngineWidget(self.fps_cap)
        self.setCentralWidget(self.viewport_widget)

    def _setup_menu(self):
        """
        Set up the menu bar actions.
        """
        self.menu_bar = self.menuBar()
        view_menu = self.menu_bar.addMenu("&View")

        self.toggle_camera_tool_panel_action = QAction("Show &Camera Tool", self)
        self.toggle_camera_tool_panel_action.setCheckable(True)
        self.toggle_camera_tool_panel_action.setChecked(True)
        self.toggle_camera_tool_panel_action.triggered.connect(
            self.toggle_camera_tool_panel_visibility
        )

        self.toggle_export_tool_panel_action = QAction("Show &Export Tool", self)
        self.toggle_export_tool_panel_action.setCheckable(True)
        self.toggle_export_tool_panel_action.setChecked(True)
        self.toggle_export_tool_panel_action.triggered.connect(
            self.toggle_export_tool_panel_visibility
        )

        view_menu.addAction(self.toggle_camera_tool_panel_action)
        view_menu.addAction(self.toggle_export_tool_panel_action)

        about_action = QAction(self, text="&About", icon=QIcon.fromTheme("help-about"))
        about_action.triggered.connect(self._show_about)

        help_menu = self.menu_bar.addMenu("&Help")
        help_menu.addAction(about_action)
        help_menu.addSeparator()
        help_menu.addAction("About &Qt", qApp.aboutQt)
        help_menu.addAction("About &Panda3D", self._show_about_panda3d)

    def _setup_status_bar(self):
        """
        Set up the status bar labels.
        """
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.fps_label = QLabel("FPS: 0")
        self.resolution_label = QLabel("Resolution: 0 x 0")

        self.fps_label.setMargin(2)
        self.resolution_label.setMargin(2)
        self.status_bar.addPermanentWidget(self.fps_label)
        self.status_bar.addPermanentWidget(self.resolution_label)

    @Slot(float)
    def _update_fps_label(self, current_fps):
        """
        Update the FPS label in the status bar.
        """
        self.fps_label.setText(f"FPS: {round(current_fps)}")

    @Slot(int, int)
    def _update_resolution_label(self, width, height):
        """
        Update the resolution label in the status bar.
        """
        self.resolution_label.setText(f"Resolution: {width} x {height}")

    def toggle_export_tool_panel_visibility(self):
        """
        Toggle the visibility of the export tool panel.
        """
        if self.export_tool_panel.isVisible():
            self.export_tool_panel.hide()
        else:
            self.export_tool_panel.show()

    def toggle_camera_tool_panel_visibility(self):
        """
        Toggle the visibility of the camera tool panel.
        """
        if self.camera_tool_panel.isVisible():
            self.camera_tool_panel.hide()
        else:
            self.camera_tool_panel.show()

    def _show_about_panda3d(self):
        """
        Create and show the AboutPanda3DDialog dialog.
        """
        about_panda_dialog = AboutPanda3DDialog()
        about_panda_dialog.exec()

    def _show_about(self):
        """
        Create and show the AboutDialog dialog.
        """
        about_dialog = AboutDialog()
        about_dialog.exec()

    def closeEvent(self, event):
        """
        Make sure the engine shuts down before closing.
        """
        if self.viewport_widget:
            self.viewport_widget.close()

        super().closeEvent(event)
