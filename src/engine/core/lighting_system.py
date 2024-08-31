import os

from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    Filename,
    Material,
    Point3,
    Texture,
    TransparencyAttrib,
    Vec4,
)


class LightingSystem:
    def __init__(self, engine):
        self.engine = engine
        self.indicator_model = None
        self.indicator_instances = []
        self.lighting_enabled = True
        self.indicators_enabled = True

        self.light_positions = {
            "key_light": (2.5, -5, 7.5),
            "fill_light": (-2.5, -2.5, 5),
            "rim_light": (0, 5, 5),
        }
        self.light_orientations = {
            "key_light": (0, 0, 5),
            "fill_light": (0, 0, 5),
            "rim_light": (0, 0, 5),
        }

        self._setup_lighting()

    def clear_lighting(self):
        """Clear all lighting and indicator models."""
        self.engine.render.clearLight()
        self._clear_indicators()

    def _setup_lighting(self):
        """Initialize and configure all lighting components."""
        if not self.lighting_enabled:
            return

        self.engine.render.clearLight()
        self._load_indicator_model()
        self._create_lights()
        if self.indicators_enabled:
            self._place_indicators()

    def _clear_indicators(self):
        """Remove all indicator models."""
        for indicator_instance in self.indicator_instances:
            indicator_instance.removeNode()
        self.indicator_instances.clear()

    def _load_indicator_model(self):
        """Load and configure the indicator model for visualizing lights."""
        model_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ),
            "resources",
            "DirectionalLight.glb",
        )
        pandafile = Filename.fromOsSpecific(model_path)
        self.indicator_model = self.engine.loader.loadModel(pandafile)

        self.indicator_model.setColor(239 / 255, 102 / 255, 60 / 255, 1)
        self.indicator_model.setScale(1)

    def _create_lights(self):
        """Create and position all lights."""
        self.key_light_np = self._create_light(
            "key_light", Vec4(1.0, 0.9, 0.8, 1), True
        )

        self.fill_light_np = self._create_light(
            "fill_light", Vec4(0.7, 0.7, 0.9, 1), False
        )

        self.rim_light_np = self._create_light(
            "rim_light", Vec4(0.9, 0.9, 1.0, 1), False
        )

        self._create_ambient_light()

    def _create_light(self, name, color, shadow_caster):
        """Helper method to create a directional light."""
        light = DirectionalLight(name)
        light_np = self.engine.render.attachNewNode(light)
        light_np.setPos(self.light_positions[name])
        light_np.lookAt(Point3(self.light_orientations[name]))
        light.setColor(color)
        light.setShadowCaster(shadow_caster)
        self.engine.render.setLight(light_np)
        return light_np

    def _create_ambient_light(self):
        """Create and position the ambient light."""
        ambient_light = AmbientLight("ambient_light")
        ambient_light.setColor(Vec4(0.3, 0.3, 0.3, 1))
        ambient_light_np = self.engine.render.attachNewNode(ambient_light)
        self.engine.render.setLight(ambient_light_np)

    def _place_indicators(self):
        """Place indicators for each light."""
        for name, light_np in [
            ("key_light", self.key_light_np),
            ("fill_light", self.fill_light_np),
            ("rim_light", self.rim_light_np),
        ]:
            self._add_light_indicator(light_np)

    def _add_light_indicator(self, light_np):
        """Add an indicator model to visualize the position and direction of a light."""
        if self.indicators_enabled and self.indicator_model:
            indicator_instance = self.indicator_model.copyTo(self.engine.render)
            indicator_instance.setPos(light_np.getPos())
            indicator_instance.setHpr(light_np.getHpr())
            self.indicator_instances.append(indicator_instance)

    def enable_lighting(self):
        """Enable lighting and re-setup the lighting."""
        self.lighting_enabled = True
        self._setup_lighting()

    def disable_lighting(self):
        """Disable lighting and clear all lights."""
        self.lighting_enabled = False
        self.clear_lighting()

    def enable_indicators(self):
        """Enable indicators and re-add them to the scene."""
        self.indicators_enabled = True
        self._clear_indicators()
        if self.lighting_enabled:
            self._place_indicators()

    def disable_indicators(self):
        """Disable indicators and remove all indicator models."""
        self.indicators_enabled = False
        self._clear_indicators()
