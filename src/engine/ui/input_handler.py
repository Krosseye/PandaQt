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

    @staticmethod
    def _normalize_angle(angle):
        return angle % 360

    def _update_status_bar(self):
        if self.status_bar:
            pos = self.camera_controller.get_position()
            x, y, z = map(int, [pos.x, pos.y, pos.z])

            if self.camera_controller.mode == CameraMode.ORBIT:
                orientation = self.camera_controller.gimbal.getHpr()
            else:
                orientation = self.camera_controller.camera.getHpr()

            h, p, r = map(int, map(self._normalize_angle, orientation))

            self.status_bar.showMessage(
                f"X={x}, Y={y}, Z={z} | H={h}, P={p}, R={r}", 500
            )

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
        if event.button() in (Qt.MouseButton.MiddleButton, Qt.MouseButton.RightButton):
            self.mouse_state = MouseState.NONE
            event.accept()
        self._update_cursor(self.mouse_state)

    def handle_mouse_move(self, event: QMouseEvent):
        if self._last_mouse_pos is None:
            return

        current_pos = event.pos()
        delta_x = current_pos.x() - self._last_mouse_pos.x()
        delta_y = current_pos.y() - self._last_mouse_pos.y()

        sensitivity = 0.1
        orientation_sensitivity = 0.5

        if self.mouse_state == MouseState.MIDDLE:
            delta_x *= sensitivity
            delta_y *= -sensitivity

            if self.camera_controller.mode == CameraMode.FREE:
                self.camera_controller.move_horizontal(delta_x)
                self.camera_controller.move_vertical(delta_y)
            else:
                pos = self.camera_controller.get_position()
                self.camera_controller.set_position(
                    x=pos.x + delta_x, y=pos.y, z=pos.z + delta_y
                )

            self._update_status_bar()

        elif self.mouse_state == MouseState.RIGHT:
            delta_x *= -orientation_sensitivity
            delta_y *= -orientation_sensitivity

            if self.camera_controller.mode == CameraMode.ORBIT:
                h, p, r = self.camera_controller.gimbal.getHpr()
                self.camera_controller.set_orientation(h=h + delta_x, p=p + delta_y)
            else:
                h, p, r = self.camera_controller.camera.getHpr()
                self.camera_controller.set_orientation(h=h + delta_x, p=p + delta_y)

            self._update_status_bar()

        self._last_mouse_pos = current_pos
        event.accept()

    def handle_wheel(self, event: QWheelEvent):
        zoom_step = event.angleDelta().y() / 120

        if self.camera_controller.mode == CameraMode.FREE:
            self.camera_controller.zoom(zoom_step)
        elif self.camera_controller.mode == CameraMode.ORBIT:
            pos = self.camera_controller.get_position()
            self.camera_controller.set_position(
                x=pos.x, y=max(-50, min(50, pos.y + zoom_step)), z=pos.z
            )

        self._update_status_bar()
