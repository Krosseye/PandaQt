import logging

from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import (
    FrameBufferProperties,
    GraphicsOutput,
    GraphicsPipe,
    Texture,
    WindowProperties,
    loadPrcFileData,
)
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QImage

from .camera_controller import CameraController
from .lighting_system import LightingSystem
from .profile_manager import ProfileManager
from .scene_manager import SceneManager

logger = logging.getLogger(__name__)


class EngineBaseNotifier(QObject):
    frame_captured = Signal(QImage)
    fps_updated = Signal(float)

    def __init__(self, engine):
        super().__init__()
        self.engine = engine


class EngineBase(ShowBase):
    def __init__(self, fps_cap=60):
        super().__init__(windowType="none")
        loadPrcFileData("", "copy-texture-inverted 1")
        loadPrcFileData("", "framebuffer-srgb true")

        self.notifier = EngineBaseNotifier(self)
        self.previous_image_data = None
        self.fps_cap = fps_cap
        self.pipe = None
        self.image_data = None

        globalClock.setFrameRate(self.fps_cap)
        globalClock.setMode(self.clock.MLimited)

        fb_props = FrameBufferProperties()
        fb_props.setRgbColor(True)
        fb_props.setRgbaBits(8, 8, 8, 0)
        fb_props.setDepthBits(16)
        fb_props.setForceHardware(True)

        win_props = WindowProperties().config_properties

        flags = GraphicsPipe.BFRefuseWindow
        flags |= GraphicsPipe.BFResizeable

        self.makeDefaultPipe()

        self.win = self.graphicsEngine.makeOutput(
            self.pipe,
            "graphics_engine",
            -100,
            fb_props,
            win_props,
            flags,
        )

        self.screen_texture = Texture()
        self.screen_texture.setFormat(Texture.FRgb32)
        self.win.addRenderTexture(
            self.screen_texture, GraphicsOutput.RTM_copy_ram, GraphicsOutput.RTP_color
        )

        self.scene_manager = SceneManager(self)
        self.camera_controller = CameraController(self)
        self.lighting_system = LightingSystem(self)
        self.profile_manager = ProfileManager(self)
        self.profile_manager.use_preview_profile()

    @Slot()
    def _capture_current_frame(self, task):
        self.notifier.fps_updated.emit(round(self.clock.getAverageFrameRate()))

        tex_xsize = self.screen_texture.getXSize()
        tex_ysize = self.screen_texture.getYSize()
        width, height = tex_xsize, tex_ysize

        image_data = self.screen_texture.getRamImage().getData()

        if image_data == self.previous_image_data:
            logger.debug("Frame from buffer skipped: No changes")
            self.previous_image_data = image_data
            return task.cont

        expected_size = width * height * 4
        if len(image_data) != expected_size:
            logger.debug(
                "Frame from buffer skipped: Size mismatch between image data and expected dimensions"
            )
            return task.cont

        q_image = QImage(
            image_data,
            width,
            height,
            width * 4,
            QImage.Format_ARGB32,
        )

        self.notifier.frame_captured.emit(q_image)
        self.previous_image_data = image_data
        logger.debug("Frame from buffer captured: Size %i x %i", width, height)

        return task.cont

    @Slot()
    def start_frame_capture(self):
        self.taskMgr.add(self._capture_current_frame, "_capture_current_frame")

    @Slot(int, int)
    def update_window_size(self, width, height):
        if self.win.getXSize() != width or self.win.getYSize() != height:
            self.win.setSize(width, height)
            self.screen_texture.setXSize(width)
            self.screen_texture.setYSize(height)
            logger.debug("Resolution set to: %i x %i", width, height)

    def stop(self):
        self.screen_texture.clearRamImage()
        self.graphicsEngine.removeWindow(self.win)
        self.finalizeExit()
