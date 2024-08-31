import logging

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
        self.load_objects()

    def load_objects(self):
        self.unload_objects()

        panda_model = self.engine.loader.loadModel("models/panda")
        panda_model.reparentTo(self.engine.render)
        panda_model.setScale(0.5)
        panda_model.setPos(0, 0, 0)
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
