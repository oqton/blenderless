import math
from dataclasses import dataclass

from blenderless.blender_object import BlenderObject


@dataclass
class BlenderCamera(BlenderObject):
    camera_type: str = 'ORTHO'
    clipping_distance: float = 5000

    def object_data(self, bpy):
        if self._object_data is None:
            self._object_data = bpy.data.cameras.new(name=self.name)
            self._object_data.type = self.camera_type
            self._object_data.clip_end = self.clipping_distance
        return self._object_data


@dataclass
class SphericalCoordinateCamera(BlenderCamera):
    azimuth: float = 0
    elevation: float = 45
    theta: float = 0
    distance: float = 1

    def __post_init__(self):
        x, y, z = self.spherical_to_cartesian(float(self.distance), float(self.azimuth), float(self.elevation))
        q1 = self.camPosToQuaternion(x, y, z)
        q2 = self.camRotQuaternion(x, y, z, float(self.theta))
        self.quaternion = self.quaternionProduct(q2, q1)
        self.xyz = x, y, z

    @staticmethod
    def camPosToQuaternion(cx, cy, cz):
        q1a = 0
        q1b = 0
        q1c = math.sqrt(2) / 2
        q1d = math.sqrt(2) / 2
        camDist = math.sqrt(cx * cx + cy * cy + cz * cz)
        cx = cx / camDist
        cy = cy / camDist
        cz = cz / camDist
        t = math.sqrt(cx * cx + cy * cy)
        tx = cx / t
        ty = cy / t
        yaw = math.acos(ty)
        if tx > 0:
            yaw = 2 * math.pi - yaw
        pitch = 0
        tmp = min(max(tx * cx + ty * cy, -1), 1)
        #roll = math.acos(tx * cx + ty * cy)
        roll = math.acos(tmp)
        if cz < 0:
            roll = -roll
        # print("%f %f %f" % (yaw, pitch, roll))
        q2a, q2b, q2c, q2d = SphericalCoordinateCamera.quaternionFromYawPitchRoll(yaw, pitch, roll)
        q1 = q1a * q2a - q1b * q2b - q1c * q2c - q1d * q2d
        q2 = q1b * q2a + q1a * q2b + q1d * q2c - q1c * q2d
        q3 = q1c * q2a - q1d * q2b + q1a * q2c + q1b * q2d
        q4 = q1d * q2a + q1c * q2b - q1b * q2c + q1a * q2d
        return (q1, q2, q3, q4)

    @staticmethod
    def quaternionFromYawPitchRoll(yaw, pitch, roll):
        c1 = math.cos(yaw / 2.0)
        c2 = math.cos(pitch / 2.0)
        c3 = math.cos(roll / 2.0)
        s1 = math.sin(yaw / 2.0)
        s2 = math.sin(pitch / 2.0)
        s3 = math.sin(roll / 2.0)
        q1 = c1 * c2 * c3 + s1 * s2 * s3
        q2 = c1 * c2 * s3 - s1 * s2 * c3
        q3 = c1 * s2 * c3 + s1 * c2 * s3
        q4 = s1 * c2 * c3 - c1 * s2 * s3
        return (q1, q2, q3, q4)

    @staticmethod
    def camRotQuaternion(cx, cy, cz, theta):
        theta = theta / 180.0 * math.pi
        camDist = math.sqrt(cx * cx + cy * cy + cz * cz)
        cx = -cx / camDist
        cy = -cy / camDist
        cz = -cz / camDist
        q1 = math.cos(theta * 0.5)
        q2 = -cx * math.sin(theta * 0.5)
        q3 = -cy * math.sin(theta * 0.5)
        q4 = -cz * math.sin(theta * 0.5)
        return (q1, q2, q3, q4)

    @staticmethod
    def quaternionProduct(qx, qy):
        a = qx[0]
        b = qx[1]
        c = qx[2]
        d = qx[3]
        e = qy[0]
        f = qy[1]
        g = qy[2]
        h = qy[3]
        q1 = a * e - b * f - c * g - d * h
        q2 = a * f + b * e + c * h - d * g
        q3 = a * g - b * h + c * e + d * f
        q4 = a * h + b * g - c * f + d * e
        return (q1, q2, q3, q4)

    @staticmethod
    def spherical_to_cartesian(dist, azimuth_deg, elevation_deg):
        phi = float(elevation_deg) / 180 * math.pi
        theta = float(azimuth_deg) / 180 * math.pi
        x = (dist * math.cos(theta) * math.cos(phi))
        y = (dist * math.sin(theta) * math.cos(phi))
        z = (dist * math.sin(phi))
        return (x, y, z)
