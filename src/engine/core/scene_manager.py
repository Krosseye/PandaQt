import logging

from direct.gui.OnscreenGeom import OnscreenGeom

from ..utils.axis_maker import AxisIndicator
from ..utils.grid_maker import SceneGridMaker

logger = logging.getLogger(__name__)


class SceneManager:
    def __init__(self, engine):
        self.engine = engine
        self.scene_objects = []

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
        axis_model = self.axis_maker.get_axis_node()

        self.axis_indicator = OnscreenGeom(
            geom=axis_model,
            scale=0.125,
            pos=(
                1.1,
                0,
                0.8,
            ),
            parent=self.engine.aspect2d,
        )
        self.axis_indicator.setTransparency(True)
        self.axis_indicator.setDepthTest(True)
        self.axis_indicator.setDepthWrite(True)

        self.engine.taskMgr.add(
            self._update_axis_indicator_position, "update_axis_position"
        )

    def _update_axis_indicator_position(self, task):
        """Update the orientation of the axis indicator."""
        h, p, r = self.engine.camera_controller.get_orientation()
        p = p % 360

        if 0 <= p < 180:
            flip_z = 180
            h = -h
        else:
            flip_z = 0

        self.axis_indicator.setHpr(h, flip_z, 0)

        return task.cont

    def load_objects(self):
        self.unload_objects()

        panda_model = self.engine.loader.loadModel("models/panda")
        panda_model.reparentTo(self.engine.render)
        panda_model.setScale(0.5)
        panda_model.setPos(0, 0, 0)
        panda_model.setBin("fixed", -5)
        self.scene_objects.append(panda_model)
        logger.info("Scene objects loaded.")

    def unload_objects(self):
        if self.scene_objects:
            for obj in self.scene_objects:
                obj.remove_node()
            self.scene_objects.clear()
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
