import logging

from ..utils.axis_maker import AxisIndicator
from ..utils.grid_maker import SceneGridMaker

logger = logging.getLogger(__name__)


class SceneManager:
    def __init__(self, engine):
        self.engine = engine
        self.scene_objects = self.engine.render.attachNewNode("scene_objects")
        self.scene_objects.setBin("fixed", -5)

        self._setup_scene()

    def _setup_scene(self):
        self.grid_maker = SceneGridMaker()
        self.grid = self.grid_maker.create_grid()
        self.grid.reparentTo(self.engine.render)
        self.grid.setLightOff()
        self.grid.setBin("fixed", 0)
        self._create_axis_indicator()
        self.load_objects()

    def _create_axis_indicator(self):
        self.axis_maker = AxisIndicator(loader=self.engine.loader)
        self.axis_indicator = self.axis_maker.get_axis_node()

        axis_parent_node = self.engine.aspect2d.attachNewNode("axis_parent_node")
        axis_parent_node.setScale(0.125)
        axis_parent_node.setPos(1.1, 0, 0.8)
        axis_parent_node.reparentTo(self.engine.aspect2d)

        self.axis_indicator.reparentTo(axis_parent_node)
        self.axis_indicator.setTransparency(True)
        self.axis_indicator.setDepthTest(True)
        self.axis_indicator.setDepthWrite(True)

        self.engine.taskMgr.doMethodLater(
            0.25,
            self._set_axis_compass,
            "_set_axis_compass",
        )

    def _set_axis_compass(self, task):
        self.axis_indicator.setCompass(self.engine.camera_controller.gimbal)
        return

    def load_objects(self):
        self.unload_objects()

        panda_model = self.engine.loader.loadModel("models/panda")
        panda_model.reparentTo(self.scene_objects)
        panda_model.setScale(0.5)
        panda_model.setPos(0, 0, 0)
        logger.info("Scene objects loaded.")

    def unload_objects(self):
        if self.scene_objects.getNumChildren() > 0:
            self.scene_objects.getChildren().detach()
            logger.info("Scene objects unloaded.")

    def show_grid(self):
        self.grid.show()
        self.is_grid_visible = True
        logger.info("Scene grid shown.")

    def hide_grid(self):
        self.is_grid_visible = False
        self.grid.hide()
        logger.info("Scene grid hidden.")

    def is_grid_visible(self):
        return self.is_grid_visible

    def show_axis_indicator(self):
        self.axis_indicator.show()
        self.is_axis_indicator_visible = True
        logger.info("Axis indicator shown.")

    def hide_axis_indicator(self):
        self.is_axis_indicator_visible = False
        self.axis_indicator.hide()
        logger.info("Axis indicator hidden.")

    def is_axis_indicator_visible(self):
        return self.is_axis_indicator_visible
