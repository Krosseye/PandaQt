import logging

from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import Vec3

logger = logging.getLogger(__name__)


class CameraController:
    def __init__(self, engine):
        self.engine = engine
        self.rotation_paused = True
        self.rotation_speed = 0
        self.screen_width_scale = 1
        self.last_frame_time = 0
        self.pause_time = 0

        self._setup_camera()

    def _setup_camera(self):
        """Setup the camera."""
        self.camera = self.engine.makeCamera(self.engine.win, lens=self.engine.camLens)
        lens = self.camera.node().getLens()
        lens.setFov(75)
        self.camera.reparentTo(self.engine.scene_manager.scene_objects[0])
        self.gimbal = self.engine.render.attach_new_node("gimbal")
        self.engine.cam.reparent_to(self.gimbal)
        self.engine.cam.set_pos(0, -15, 7)
        self.gimbal.setHpr(0, 0, 0)

    def _rotate_camera_task(self, task):
        if not self.rotation_paused:
            current_time = globalClock.getRealTime()
            dt = current_time - self.last_frame_time
            self.last_frame_time = current_time

            adjusted_rotation_speed = self.rotation_speed * dt * self.screen_width_scale
            current_orientation = self.gimbal.getHpr()
            new_orientation = Vec3(
                current_orientation.x + adjusted_rotation_speed,
                current_orientation.y,
                current_orientation.z,
            )
            self.gimbal.setHpr(new_orientation)

        return task.cont

    def start_rotation(self):
        """Resume the camera auto-rotation."""
        if self.rotation_paused:
            self.last_frame_time += globalClock.getRealTime() - self.pause_time
            self.rotation_paused = False
            self.engine.taskMgr.add(
                self._rotate_camera_task, "_anim_camera_rotate", sort=49
            )
            logger.debug("Camera auto rotation started.")

    def stop_rotation(self):
        """Pause the camera auto-rotation."""
        if not self.rotation_paused:
            self.pause_time = globalClock.getRealTime()
            self.rotation_paused = True
            self.engine.taskMgr.remove("_anim_camera_rotate")
            logger.debug("Camera auto rotation stopped.")

    def update_fov(self, fov_value):
        """Set the camera's field of view."""
        lens = self.camera.node().getLens()
        lens.setFov(fov_value)
        logger.debug("Camera FOV set: %i", fov_value)

    def update_rotation_speed(self, speed):
        """Update the camera's rotation speed."""
        self.rotation_speed = speed
        logger.debug("Camera rotation speed set to: %i", speed)

    def update_orientation(self, h, p, r):
        """Update the camera's rotation around the gimbal."""
        self.gimbal.setHpr(h, p, r)
        logger.debug("Camera rotation set to: H=%i, P=%i, R=%i", h, p, r)

    def update_heading(self, h):
        """Update the camera's heading around the gimbal."""
        self.gimbal.set_h(h)
        logger.debug("Camera heading set to: %i", h)

    def update_pitch(self, p):
        """Update the camera's pitch around the gimbal."""
        self.gimbal.set_p(p)
        logger.debug("Camera pitch set to: %i", p)

    def update_roll(self, r):
        """Update the camera's roll around the gimbal."""
        self.gimbal.set_r(r)
        logger.debug("Camera roll set to: %i", r)

    def update_position_x(self, x):
        """Update the camera's x position."""
        current_pos = self.engine.cam.getPos(self.gimbal)
        self.engine.cam.setPos(self.gimbal, x, current_pos.y, current_pos.z)
        logger.debug("Camera x position set to: %i", x)

    def update_position_y(self, y):
        """Update the camera's y position."""
        current_pos = self.engine.cam.getPos(self.gimbal)
        self.engine.cam.setPos(self.gimbal, current_pos.x, y, current_pos.z)
        logger.debug("Camera y position set to: %i", y)

    def update_position_z(self, z):
        """Update the camera's z position."""
        current_pos = self.engine.cam.getPos(self.gimbal)
        self.engine.cam.setPos(self.gimbal, current_pos.x, current_pos.y, z)
        logger.debug("Camera z position set to: %i", z)
