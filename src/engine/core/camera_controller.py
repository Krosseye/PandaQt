import logging
from enum import Enum

from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import Vec3

logger = logging.getLogger(__name__)


class CameraMode(Enum):
    ORBIT = 1
    FREE = 2


class CameraController:
    def __init__(self, engine):
        self.engine = engine
        self.rotation_paused = True
        self.rotation_speed = 0
        self.screen_width_scale = 1
        self.last_frame_time = 0
        self.pause_time = 0
        self.mode = CameraMode.ORBIT
        self.camera_mode = CameraMode
        self.default_position = Vec3(0, -15, 3)
        self.default_hpr = Vec3(0, 0, 0)

        self._setup_camera()

    def _setup_camera(self):
        """Setup the camera."""
        self.camera = self.engine.makeCamera(self.engine.win, lens=self.engine.camLens)
        lens = self.camera.node().getLens()
        lens.setFov(50)

        self.gimbal = self.engine.render.attach_new_node("gimbal")
        self.camera.reparentTo(self.gimbal)
        self.camera.set_pos(self.default_position)
        self.gimbal.setHpr(self.default_hpr)

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
            if self.mode == CameraMode.FREE:
                self.camera.setHpr(new_orientation)

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

    def set_mode(self, mode):
        """Set the camera mode."""
        self.camera.setPos(self.default_position)
        self.camera.setHpr(self.default_hpr)
        self.gimbal.setHpr(self.default_hpr)
        self.mode = mode

        if mode == CameraMode.ORBIT:
            self.camera.reparentTo(self.gimbal)
            logger.debug("Camera mode set to ORBIT.")
        elif mode == CameraMode.FREE:
            self.camera.wrtReparentTo(self.engine.render)
            logger.debug("Camera mode set to FREE.")

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
        if self.mode == CameraMode.ORBIT:
            self.gimbal.setHpr(h, p, r)
        else:
            self.gimbal.setHpr(h, p, r)
            self.camera.setHpr(h, p, r)
        logger.debug("Camera rotation set to: H=%i, P=%i, R=%i", h, p, r)

    def update_heading(self, h):
        """Update the camera's heading."""
        if self.mode == CameraMode.ORBIT:
            self.gimbal.set_h(h)
        else:
            self.gimbal.set_h(h)
            self.camera.set_h(h)
        logger.debug("Camera heading set to: %i", h)

    def update_pitch(self, p):
        """Update the camera's pitch."""
        if self.mode == CameraMode.ORBIT:
            self.gimbal.set_p(p)
        else:
            self.gimbal.set_p(p)
            self.camera.set_p(p)
        logger.debug("Camera pitch set to: %i", p)

    def update_roll(self, r):
        """Update the camera's roll."""
        if self.mode == CameraMode.ORBIT:
            self.gimbal.set_r(r)
        else:
            self.gimbal.set_r(r)
            self.camera.set_r(r)
        logger.debug("Camera roll set to: %i", r)

    def update_position_x(self, x):
        """Update the camera's x position."""
        if self.mode == CameraMode.ORBIT:
            current_pos = self.camera.getPos(self.gimbal)
            self.camera.setPos(self.gimbal, x, current_pos.y, current_pos.z)
        else:
            current_pos = self.camera.getPos()
            self.camera.setPos(x, current_pos.y, current_pos.z)
        logger.debug("Camera x position set to: %i", x)

    def update_position_y(self, y):
        """Update the camera's y position."""
        if self.mode == CameraMode.ORBIT:
            current_pos = self.camera.getPos(self.gimbal)
            self.camera.setPos(self.gimbal, current_pos.x, y, current_pos.z)
        else:
            current_pos = self.camera.getPos()
            self.camera.setPos(current_pos.x, y, current_pos.z)
        logger.debug("Camera y position set to: %i", y)

    def update_position_z(self, z):
        """Update the camera's z position."""
        if self.mode == CameraMode.ORBIT:
            current_pos = self.camera.getPos(self.gimbal)
            self.camera.setPos(self.gimbal, current_pos.x, current_pos.y, z)
        else:
            current_pos = self.camera.getPos()
            self.camera.setPos(current_pos.x, current_pos.y, z)
        logger.debug("Camera z position set to: %i", z)

    def update_position(self, position):
        """Update the camera's position."""
        x, y, z = position
        if self.mode == CameraMode.ORBIT:
            self.camera.setPos(self.gimbal, x, y, z)
        else:
            self.camera.setPos(x, y, z)
        logger.debug("Camera position set to: %i,%i,%i", x, y, z)

    def get_position(self):
        current_pos = (
            self.camera.getPos(self.gimbal)
            if self.mode == CameraMode.ORBIT
            else self.camera.getPos()
        )
        return current_pos

    def move_vertical(self, distance):
        """Move the camera vertiacl relative to its current orientation."""
        if self.mode == CameraMode.FREE:
            up_vector = Vec3(0, 0, 1)
            move_vector = self.camera.getMat().xform_vec(up_vector) * distance
            new_pos = self.camera.getPos() + move_vector
            self.camera.setPos(new_pos)
            logger.debug("Camera moved vertiacl by: %i", distance)

    def move_horizontal(self, distance):
        """Move the camera horizontal relative to its current orientation."""
        if self.mode == CameraMode.FREE:
            left_vector = Vec3(1, 0, 0)
            move_vector = self.camera.getMat().xform_vec(left_vector) * distance
            new_pos = self.camera.getPos() + move_vector
            self.camera.setPos(new_pos)
            logger.debug("Camera moved horizontal by: %i", distance)

    def zoom(self, distance):
        """Zoom the camera relative to its current orientation."""
        if self.mode == CameraMode.FREE:
            forward_vector = Vec3(0, 1, 0) if distance > 0 else Vec3(0, -1, 0)
            move_vector = self.camera.getMat().xform_vec(forward_vector) * abs(distance)
            new_pos = self.camera.getPos() + move_vector
            self.camera.setPos(new_pos)
            logger.debug("Camera zoomed by: %i", distance)
