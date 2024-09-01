from enum import Enum

from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QWidget

from ..core.camera_controller import CameraMode


class MouseState(Enum):
    NONE = 0
    MIDDLE = 1
    RIGHT = 2


class InputHandler:
    def __init__(self, widget: QWidget):
        self.widget = widget
        self.engine = widget.engine
        self.camera_controller = self.engine.camera_controller
        self.status_bar = widget.status_bar

        self.mouse_state = MouseState.NONE
        self._last_mouse_pos = None

    def _update_cursor(self, state: MouseState):
        cursor_map = {
            MouseState.NONE: Qt.CursorShape.ArrowCursor,
            MouseState.MIDDLE: Qt.CursorShape.SizeAllCursor,
            MouseState.RIGHT: Qt.CursorShape.ClosedHandCursor,
        }
        self.widget.setCursor(cursor_map.get(state, Qt.CursorShape.ArrowCursor))

    def _update_status_bar(self):
        if self.status_bar:
            new_position = self.camera_controller.get_position()
            x, y, z = map(int, [new_position.x, new_position.y, new_position.z])
            self.status_bar.showMessage(f"X={x}, Y={y}, Z={z}", 500)

    def handle_mouse_press(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.mouse_state = MouseState.MIDDLE
            self._last_mouse_pos = event.pos()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.mouse_state = MouseState.RIGHT
            self._last_mouse_pos = event.pos()
            event.accept()
        self._update_cursor(self.mouse_state)

    def handle_mouse_release(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.mouse_state = MouseState.NONE
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.mouse_state = MouseState.NONE
            event.accept()
        self._update_cursor(self.mouse_state)

    def handle_mouse_move(self, event: QMouseEvent):
        if self._last_mouse_pos is None:
            return

        current_pos = event.pos()
        delta_x = current_pos.x() - self._last_mouse_pos.x()
        delta_y = current_pos.y() - self._last_mouse_pos.y()

        if self.mouse_state == MouseState.MIDDLE:
            delta_x *= 0.1
            delta_y *= -0.1

            if self.camera_controller.mode == CameraMode.FREE:
                self.camera_controller.move_horizontal(delta_x)
                self.camera_controller.move_vertical(delta_y)
            else:
                camera_pos = self.camera_controller.get_position()
                self.camera_controller.update_position_x(camera_pos.x + delta_x)
                self.camera_controller.update_position_z(camera_pos.z + delta_y)

            self._update_status_bar()

        elif self.mouse_state == MouseState.RIGHT:
            delta_x *= -1
            delta_y *= -1

            if self.camera_controller.mode == CameraMode.ORBIT:
                h, p, r = self.camera_controller.gimbal.getHpr()
                self.camera_controller.update_heading((h + delta_x) % 360)
                self.camera_controller.update_pitch((p + delta_y) % 360)
            else:
                h, p, r = self.camera_controller.camera.getHpr()
                self.camera_controller.camera.setHpr(
                    (h + delta_x) % 360, (p + delta_y) % 360, r
                )

            if self.status_bar:
                new_orientation = (
                    self.camera_controller.gimbal.getHpr()
                    if self.camera_controller.mode == CameraMode.ORBIT
                    else self.camera_controller.camera.getHpr()
                )
                h, p, r = map(int, new_orientation)
                self.status_bar.showMessage(f"H={h}, P={p}, R={r}", 500)

        self._last_mouse_pos = current_pos
        event.accept()

    def handle_wheel(self, event: QWheelEvent):
        zoom_step = event.angleDelta().y() / 120

        if self.camera_controller.mode == CameraMode.FREE:
            self.camera_controller.zoom(zoom_step)
        elif self.camera_controller.mode == CameraMode.ORBIT:
            camera_pos = self.camera_controller.get_position()
            new_y_position = max(-50, min(50, camera_pos.y + zoom_step))
            if new_y_position != camera_pos.y:
                self.camera_controller.update_position_y(new_y_position)

        self._update_status_bar()
