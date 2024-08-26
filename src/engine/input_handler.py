from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QWidget


class InputHandler:
    def __init__(self, widget: QWidget):
        self.widget = widget
        self.engine = widget.engine
        self.status_bar = widget.status_bar

        self._right_mouse_pressed = False
        self._middle_mouse_pressed = False
        self._last_mouse_pos = None
        self._zoom_level = 0

    def handle_mouse_press(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._middle_mouse_pressed = True
            self._last_mouse_pos = event.pos()
            self.widget.setCursor(Qt.CursorShape.SizeAllCursor)
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self._right_mouse_pressed = True
            self.widget.setCursor(Qt.CursorShape.ClosedHandCursor)
            self._last_mouse_pos = event.pos()
            event.accept()

    def handle_mouse_release(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._middle_mouse_pressed = False
            self.widget.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self._right_mouse_pressed = False
            self.widget.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()

    def handle_mouse_move(self, event: QMouseEvent):
        if self._middle_mouse_pressed:
            current_pos = event.pos()
            if self._last_mouse_pos is not None:
                delta_x = current_pos.x() - self._last_mouse_pos.x()
                delta_y = current_pos.y() - self._last_mouse_pos.y()

                scale_factor = 0.1
                delta_x = delta_x * scale_factor
                delta_y = -delta_y * scale_factor

                camera_pos = self.engine.camera_controller.get_position()

                self.engine.camera_controller.update_position_x(camera_pos.x + delta_x)
                self.engine.camera_controller.update_position_z(camera_pos.z + delta_y)

                if self.status_bar is not None:
                    new_position = self.engine.camera_controller.get_position()
                    x = int(new_position.x)
                    y = int(new_position.y)
                    z = int(new_position.z)
                    self.status_bar.showMessage(f"X={x}, Y={y}, Z={z}", 500)

            self._last_mouse_pos = current_pos
            event.accept()

        elif self._right_mouse_pressed:
            current_pos = event.pos()
            if self._last_mouse_pos is not None:
                delta_x = -(current_pos.x() - self._last_mouse_pos.x())
                delta_y = -(current_pos.y() - self._last_mouse_pos.y())

                h, p, r = self.engine.camera_controller.gimbal.getHpr()

                new_heading = (h + delta_x) % 360
                new_pitch = (p + delta_y) % 360

                self.engine.camera_controller.update_heading(new_heading)
                self.engine.camera_controller.update_pitch(new_pitch)

                if self.status_bar is not None:
                    new_orientation = self.engine.camera_controller.gimbal.getHpr()
                    h, p, r = new_orientation
                    self.status_bar.showMessage(
                        f"H={int(h)}, P={int(p)}, R={int(r)}", 500
                    )

            self._last_mouse_pos = current_pos
            event.accept()

    def handle_wheel(self, event: QWheelEvent):
        zoom_step = 1 if event.angleDelta().y() > 0 else -1

        camera_pos = self.engine.camera_controller.get_position()
        current_y = camera_pos.y
        new_y_position = current_y + zoom_step
        clamped_y_position = max(-50, min(50, new_y_position))
        if clamped_y_position != current_y:
            self.engine.camera_controller.update_position_y(clamped_y_position)

            if self.status_bar is not None:
                new_position = self.engine.camera_controller.get_position()
                x = int(new_position.x)
                y = int(new_position.y)
                z = int(new_position.z)
                self.status_bar.showMessage(f"X={x}, Y={y}, Z={z}", 500)
