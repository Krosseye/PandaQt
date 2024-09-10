import logging

from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import (
    Camera,
    FrameBufferProperties,
    GraphicsOutput,
    GraphicsPipe,
    OrthographicLens,
    Texture,
    WindowProperties,
    loadPrcFileData,
)
from PySide6.QtCore import QObject, QTimer, Signal, Slot
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QMessageBox

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
    def __init__(self, fps_cap=60, enable_hd_renderer=False):
        super().__init__(windowType="none")
        loadPrcFileData("", "copy-texture-inverted 1")
        loadPrcFileData("", "framebuffer-srgb true")

        self.notifier = EngineBaseNotifier(self)
        self.previous_image_data = None
        self.fps_cap = fps_cap
        self.pipe = None
        self.image_data = None
        self.capture_timer = None

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

        self.cam2d_node = Camera("cam2d")
        self.cam2d = self.render2d.attachNewNode(self.cam2d_node)

        lens = OrthographicLens()
        lens.setFilmSize(2, 2)
        lens.setNearFar(-1, 1000)
        self.cam2d_node.setLens(lens)

        aspect2d_region = self.win.makeDisplayRegion()
        aspect2d_region.setCamera(self.cam2d)
        aspect2d_region.setSort(20)

        self.scene_manager = SceneManager(self)
        self.camera_controller = CameraController(self)
        self.lighting_system = LightingSystem(self)
        self.profile_manager = ProfileManager(self)
        self.profile_manager.use_preview_profile()

        if enable_hd_renderer:
            self._setup_hd_pipeline()

        self._setup_timer()

    def _setup_hd_pipeline(self):
        try:
            import simplepbr

            self.pipeline = simplepbr.init(exposure=1, msaa_samples=0)
            loadPrcFileData("", "copy-texture-inverted 0")
            self.pipeline._filtermgr.buffers[0].setClearColor(
                (61 / 255, 61 / 255, 61 / 255, 1)
            )
            logger.info("HD Renderer enabled.")
        except ImportError:
            _message = str(
                "The HD Renderer could not be initialized, "
                + "your device may not support it.\n\n"
                + "The program will fall back to the built-in renderer."
            )

            message_box = QMessageBox(
                QMessageBox.Warning,
                "HD Renderer Unavailable",
                _message,
                QMessageBox.Ok,
            )
            logger.warning(_message.replace("\n\n", " "))
            message_box.exec()

    def _setup_timer(self):
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self._capture_current_frame)
        self.capture_timer.setInterval(round(1000 / self.fps_cap))

    @Slot()
    def _capture_current_frame(self):
        self.notifier.fps_updated.emit(round(self.clock.getAverageFrameRate()))

        tex_xsize = self.screen_texture.getXSize()
        tex_ysize = self.screen_texture.getYSize()
        width, height = tex_xsize, tex_ysize

        image_data = self.screen_texture.getRamImage().getData()

        if image_data == self.previous_image_data:
            logger.debug("Frame from buffer skipped: No changes")
            self.previous_image_data = image_data
            return

        expected_size = width * height * 4
        if len(image_data) != expected_size:
            logger.debug(
                "Frame from buffer skipped: Size mismatch between image data and expected dimensions"
            )
            return

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

    @Slot()
    def start_frame_capture(self):
        if self.capture_timer is not None:
            self.capture_timer.start()

    @Slot()
    def stop_frame_capture(self):
        if self.capture_timer is not None:
            self.capture_timer.stop()

    @Slot(int, int)
    def update_window_size(self, width, height):
        if self.win.getXSize() != width or self.win.getYSize() != height:
            self.win.setSize(width, height)
            self.screen_texture.setXSize(width)
            self.screen_texture.setYSize(height)
            logger.debug("Resolution set to: %i x %i", width, height)

    def stop(self):
        self.stop_frame_capture()
        self.screen_texture.clearRamImage()
        self.graphicsEngine.removeWindow(self.win)
        self.finalizeExit()
