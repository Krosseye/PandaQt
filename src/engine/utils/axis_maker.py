import os

from panda3d.core import (
    BillboardEffect,
    CardMaker,
    Filename,
    LColor,
    LineSegs,
    NodePath,
    Vec3,
)


class AxisIndicator:
    """
    A class to create a 3D axis indicator with labeled axes (X, Y, Z).
    """

    def __init__(self, loader=None):
        """
        Initializes the AxisIndicator class.
        """
        self.root = NodePath("axis_indicator")
        self.loader = loader
        self.line_segs = LineSegs()

        self._create_axis(
            direction=Vec3(0.75, 0, 0),
            color=LColor(230 / 255, 55 / 255, 80 / 255, 1),
            label="X",
        )
        self._create_axis(
            direction=Vec3(0, 0.75, 0),
            color=LColor(124 / 255, 189 / 255, 19 / 255, 1),
            label="Y",
        )
        self._create_axis(
            direction=Vec3(0, 0, 0.75),
            color=LColor(45 / 255, 139 / 255, 246 / 255, 1),
            label="Z",
        )

    def _create_axis(self, direction, color, label):
        """
        Creates an axis line in a given direction and labels it with a circle.
        """
        self.line_segs.set_color(color)
        self.line_segs.set_thickness(2)
        self.line_segs.move_to(0, 0, 0)
        self.line_segs.draw_to(direction)

        self._create_circle(
            position=direction * 1.25, texture_file=f"{label}.png", color=color
        )
        self._create_circle(
            position=-direction * 1.25, texture_file="circle_border.png", color=color
        )

    def _create_circle(self, position, texture_file, color):
        """
        Creates a labeled circle that represents the axis label. The circle always faces the camera.
        """
        card_maker = CardMaker("circle")
        card_maker.set_frame(-0.5, 0.5, -0.5, 0.5)
        circle_node = self.root.attach_new_node(card_maker.generate())

        if self.loader:
            texture_path = os.path.join(
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                ),
                "resources",
                "textures",
                texture_file,
            )
            texture = self.loader.load_texture(Filename.from_os_specific(texture_path))
            circle_node.set_texture(texture)

        circle_node.set_scale(0.5)
        circle_node.set_pos(position)
        circle_node.set_color(color)

        circle_node.set_effect(BillboardEffect.make_point_eye())

    def get_axis_node(self):
        """
        Returns the NodePath containing the axis lines and labels.
        """
        axis_geom_node = self.line_segs.create()
        axis_geom_np = self.root.attach_new_node(axis_geom_node)
        return self.root
