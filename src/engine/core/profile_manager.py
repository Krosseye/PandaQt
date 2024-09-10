import logging

from direct.showbase.ShowBase import ShowBase
from panda3d.core import AntialiasAttrib

logger = logging.getLogger(__name__)

ANTIALIAS_NONE = 0
ANTIALIAS_2X = 2
ANTIALIAS_4X = 4
ANTIALIAS_8X = 8
ANTIALIAS_16X = 16
VALID_ALIASING_LEVELS = {ANTIALIAS_2X, ANTIALIAS_4X, ANTIALIAS_8X, ANTIALIAS_16X}


class ProfileManager:
    def __init__(self, engine: ShowBase):
        """
        Initializes the ProfileManager with the given engine.
        """
        self.engine = engine
        self.scene_manager = engine.scene_manager
        self.lighting_system = engine.lighting_system

        if not self.scene_manager:
            raise RuntimeError("SceneManager is not properly initialized.")
        if not self.lighting_system:
            raise RuntimeError("LightingSystem is not properly initialized.")

        self._initialize_render_settings()

        self._indicators_enabled = self.lighting_system.indicators_enabled
        self._grid_visible = self.scene_manager.is_grid_visible()

    def _initialize_render_settings(self):
        """Initializes the render settings to default values."""
        self._clear_antialias()

    def _clear_antialias(self):
        """Clears antialias settings and sets to None."""
        self.engine.render.clearAntialias()
        self.engine.render.setAntialias(AntialiasAttrib.MNone)

    def _set_antialias(self, aliasing_level: int):
        """
        Sets the antialiasing level for the render.
        """
        if aliasing_level in VALID_ALIASING_LEVELS:
            self.engine.render.clearAntialias()
            self.engine.render.setAntialias(
                AntialiasAttrib.MMultisample, aliasing_level
            )
            logger.info(f"Antialiasing set to {aliasing_level}x.")
        elif aliasing_level == ANTIALIAS_NONE:
            self._clear_antialias()
        else:
            logger.error(
                f"Invalid antialiasing value: {aliasing_level}. Valid values are {VALID_ALIASING_LEVELS}."
            )

    def use_preview_profile(self):
        """Sets up the preview profile."""
        self._clear_antialias()
        self.scene_manager.show_grid()
        self.scene_manager.show_axis_indicator()

        if self._indicators_enabled:
            self.lighting_system.enable_indicators()
        else:
            self.lighting_system.disable_indicators()

        logger.info("Preview profile activated.")

    def use_export_profile(self, aliasing_level: int):
        """
        Sets up the export profile.
        """
        self._set_antialias(aliasing_level)
        self.scene_manager.hide_grid()
        self.scene_manager.hide_axis_indicator()

        self._indicators_enabled = self.lighting_system.indicators_enabled

        self.lighting_system.disable_indicators()

        logger.info(
            "Export profile activated with antialiasing level %d.", aliasing_level
        )

    def restore_profile(self):
        """Restores the profile to the previously saved state."""
        if self._indicators_enabled:
            self.lighting_system.enable_indicators()
        else:
            self.lighting_system.disable_indicators()

        if self._grid_visible:
            self.scene_manager.show_grid()
        else:
            self.scene_manager.hide_grid()

        logger.info("Profile restored with previous state.")

    def update_state_tracking(self):
        """Updates internal tracking state."""
        self._indicators_enabled = self.lighting_system.indicators_enabled
        self._grid_visible = self.scene_manager.is_grid_visible()
