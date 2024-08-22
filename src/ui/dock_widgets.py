import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget

from .panels.camera_tool import CameraControlsWidget
from .panels.export_tool import ImageExportWidget

logger = logging.getLogger(__name__)


def setup_docks(main_window):
    """Set up dock widgets for the main window."""
    _create_camera_tool_dock(main_window)
    _create_export_tool_dock(main_window)


def _create_camera_tool_dock(main_window):
    main_window.camera_tool_panel = QDockWidget("Camera Tool", main_window)
    main_window.camera_tool_panel.setFeatures(
        QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable
    )
    main_window.camera_tool_panel.setWidget(
        CameraControlsWidget(main_window.viewport_widget.engine)
    )
    main_window.camera_tool_panel.setAllowedAreas(
        Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea
    )
    main_window.addDockWidget(Qt.LeftDockWidgetArea, main_window.camera_tool_panel)


def _create_export_tool_dock(main_window):
    main_window.export_tool_panel = QDockWidget("Export Tool", main_window)
    main_window.export_tool_panel.setFeatures(
        QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable
    )
    main_window.export_tool_panel.setWidget(
        ImageExportWidget(main_window.viewport_widget, main_window.status_bar)
    )
    main_window.export_tool_panel.setAllowedAreas(
        Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea
    )
    main_window.addDockWidget(Qt.RightDockWidgetArea, main_window.export_tool_panel)
