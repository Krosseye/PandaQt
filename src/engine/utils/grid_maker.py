"""
Adapted from Mathew Lloyd/'Forklift's 'Procedural Coordinate Grid' example
https://discourse.panda3d.org/t/procedurally-generated-three-plane-coordinate-grid/4415
"""

from panda3d.core import LineSegs, NodePath, PandaNode, VBase4


class SceneGridMaker:
    def __init__(
        self,
        show_xy_plane=True,
        show_endcap_lines=True,
        x_size=4,
        y_size=4,
        grid_step=2,
        subdivisions=4,
    ):
        self.axis_lines = LineSegs()
        self.grid_lines = LineSegs()
        self.subdivision_lines = LineSegs()

        self.x_size = x_size
        self.y_size = y_size
        self.grid_step = grid_step
        self.subdivisions = subdivisions

        self.show_xy_plane = show_xy_plane
        self.show_endcap_lines = show_endcap_lines
        self.x_axis_color = VBase4(230 / 255, 55 / 255, 80 / 255, 1)
        self.y_axis_color = VBase4(124 / 255, 189 / 255, 19 / 255, 1)
        self.grid_color = VBase4(123 / 255, 123 / 255, 123 / 255, 1)
        self.subdivision_color = VBase4(84 / 255, 84 / 255, 84 / 255, 1)

        self.axis_thickness = 2
        self.grid_thickness = 0.5
        self.subdivision_thickness = 1

    def create_grid(self):
        self.axis_lines.setThickness(self.axis_thickness)
        self.grid_lines.setThickness(self.grid_thickness)
        self.subdivision_lines.setThickness(self.subdivision_thickness)

        self._draw_axes()
        self._draw_primary_grid_lines()
        self._draw_secondary_grid_lines()

        return self._create_node_path()

    def _draw_axes(self):
        # Draw X axis line
        if self.x_size != 0:
            self.axis_lines.setColor(self.x_axis_color)
            self.axis_lines.moveTo(-self.x_size, 0, 0)
            self.axis_lines.drawTo(self.x_size, 0, 0)

        # Draw Y axis line
        if self.y_size != 0:
            self.axis_lines.setColor(self.y_axis_color)
            self.axis_lines.moveTo(0, -self.y_size, 0)
            self.axis_lines.drawTo(0, self.y_size, 0)

    def _draw_primary_grid_lines(self):
        if self.grid_step == 0:
            return

        self.grid_lines.setColor(self.grid_color)

        if self.x_size != 0:
            self._draw_xy_plane_grid()

    def _draw_xy_plane_grid(self):
        if self.show_xy_plane:
            # Draw Y lines across X axis (XY Plane)
            for x in self._frange(0, self.x_size, self.grid_step):
                if x != 0:
                    self.grid_lines.moveTo(x, -self.y_size, 0)
                    self.grid_lines.drawTo(x, self.y_size, 0)
                    self.grid_lines.moveTo(-x, -self.y_size, 0)
                    self.grid_lines.drawTo(-x, self.y_size, 0)

            if self.show_endcap_lines:
                self.grid_lines.moveTo(self.x_size, -self.y_size, 0)
                self.grid_lines.drawTo(self.x_size, self.y_size, 0)
                self.grid_lines.moveTo(-self.x_size, -self.y_size, 0)
                self.grid_lines.drawTo(-self.x_size, self.y_size, 0)

            # Draw X lines across Y axis (XY Plane)
            for y in self._frange(0, self.y_size, self.grid_step):
                if y != 0:
                    self.grid_lines.moveTo(-self.x_size, y, 0)
                    self.grid_lines.drawTo(self.x_size, y, 0)
                    self.grid_lines.moveTo(-self.x_size, -y, 0)
                    self.grid_lines.drawTo(self.x_size, -y, 0)

            if self.show_endcap_lines:
                self.grid_lines.moveTo(-self.x_size, self.y_size, 0)
                self.grid_lines.drawTo(self.x_size, self.y_size, 0)
                self.grid_lines.moveTo(-self.x_size, -self.y_size, 0)
                self.grid_lines.drawTo(self.x_size, -self.y_size, 0)

    def _draw_secondary_grid_lines(self):
        if self.subdivisions == 0:
            return

        self.subdivision_lines.setColor(self.subdivision_color)
        adjusted_step = self.grid_step / self.subdivisions

        if self.x_size != 0:
            self._draw_xy_plane_subdivisions(adjusted_step)

    def _draw_xy_plane_subdivisions(self, adjusted_step):
        if self.show_xy_plane:
            # Draw Y lines across X axis (XY Plane)
            for x in self._frange(0, self.x_size, adjusted_step):
                if x != 0:
                    self.subdivision_lines.moveTo(x, -self.y_size, 0)
                    self.subdivision_lines.drawTo(x, self.y_size, 0)
                    self.subdivision_lines.moveTo(-x, -self.y_size, 0)
                    self.subdivision_lines.drawTo(-x, self.y_size, 0)

            # Draw X lines across Y axis (XY Plane)
            for y in self._frange(0, self.y_size, adjusted_step):
                if y != 0:
                    self.subdivision_lines.moveTo(-self.x_size, y, 0)
                    self.subdivision_lines.drawTo(self.x_size, y, 0)
                    self.subdivision_lines.moveTo(-self.x_size, -y, 0)
                    self.subdivision_lines.drawTo(self.x_size, -y, 0)

    def _create_node_path(self):
        grid_node_path = NodePath(PandaNode("grid"))
        grid_node_path.attachNewNode(self.axis_lines.create())
        grid_node_path.attachNewNode(self.grid_lines.create())
        grid_node_path.attachNewNode(self.subdivision_lines.create())

        return grid_node_path

    def _frange(self, start, stop, step):
        current = start
        while current <= stop:
            yield current
            current += step
