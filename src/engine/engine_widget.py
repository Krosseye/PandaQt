import logging
import time

from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QImage, QMouseEvent, QPainter, QPixmap, QWheelEvent
from PySide6.QtWidgets import QWidget

from .engine_base import EngineBase
from .input_handler import InputHandler

logger = logging.getLogger(__name__)


class EngineWidget(QWidget):
    size_changed = Signal(int, int)

    def __init__(self, fps_cap, min_width=250, status_bar=None):
        super().__init__()
        palette = self.palette()
        palette.setColor(self.backgroundRole(), "#3c3c3c")
        self.setAutoFillBackground(True)
        self.setPalette(palette)
        self.setMinimumWidth(min_width)

        self._width, self._height = self.size().width(), self.size().height()
        self.engine = EngineBase(fps_cap)
        self.pixmap = QPixmap()
        self.status_bar = status_bar

        self.is_resizing = False
        self.frame_captured_timestamp = 0
        self.frame_displayed_timestamp = 0

        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self._emit_resize_event)

        self.engine.update_window_size(self._width, self._height)
        self.engine.start_frame_capture()

        self.engine.notifier.frame_captured.connect(self._on_frame_captured)
        self.size_changed.connect(self.engine.update_window_size)

        self.input_handler = InputHandler(self)

    def paintEvent(self, event):
        if self.pixmap.isNull():
            return
        painter = QPainter(self)
        self._draw_pixmap(painter, self.pixmap)
        painter.end()
        self._update_timestamps()

    def resizeEvent(self, event):
        self._handle_resize(event.size().width(), event.size().height())

    def closeEvent(self, event):
        self.engine.stop()
        self.engine = None
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        self.input_handler.handle_mouse_press(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.input_handler.handle_mouse_release(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        self.input_handler.handle_mouse_move(event)

    def wheelEvent(self, event: QWheelEvent):
        self.input_handler.handle_wheel(event)

    @Slot(QImage)
    def _on_frame_captured(self, q_image: QImage):
        self.frame_captured_timestamp = time.time() * 1000
        self.pixmap = QPixmap.fromImage(q_image)
        self.update()

    def _emit_resize_event(self):
        if self.is_resizing:
            self.size_changed.emit(self._width, self._height)
            self.is_resizing = False

    def _handle_resize(self, new_width, new_height):
        if new_width != self._width or new_height != self._height:
            self._width, self._height = new_width, new_height
            self.is_resizing = True
            self.resize_timer.start(200)

    def _update_timestamps(self):
        self.frame_displayed_timestamp = time.time() * 1000
        if self.frame_captured_timestamp:
            duration = self.frame_displayed_timestamp - self.frame_captured_timestamp
            logger.debug("Time taken to display frame: %.2f ms", duration)

    def _draw_pixmap(self, painter, pixmap):
        widget_width, widget_height = self.width(), self.height()
        pixmap_rect = pixmap.rect()
        pixmap_width, pixmap_height = pixmap_rect.width(), pixmap_rect.height()

        scaled_pixmap = pixmap.scaled(
            widget_width, widget_height, Qt.AspectRatioMode.KeepAspectRatioByExpanding
        )
        scaled_pixmap_width, scaled_pixmap_height = (
            scaled_pixmap.width(),
            scaled_pixmap.height(),
        )

        if (pixmap_width, pixmap_height) != (widget_width, widget_height):
            x_offset = (widget_width - scaled_pixmap_width) / 2
            y_offset = (widget_height - scaled_pixmap_height) / 2
            painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
        else:
            x_offset = (widget_width - pixmap_width) / 2
            y_offset = (widget_height - pixmap_height) / 2
            painter.drawPixmap(x_offset, y_offset, pixmap)
