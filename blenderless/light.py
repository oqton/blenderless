from dataclasses import dataclass

import bpy

from blenderless import utils
from blenderless.blender_object import BlenderObject


@dataclass
class BlenderLight(BlenderObject):
    energy: float = 50
    type: str = 'POINT'

    def object_data(self):
        if self._object_data is None:
            self._object_data = bpy.data.lights.new(name=self.name, type=self.type)
            self._object_data.energy = self.energy
        return self._object_data


@dataclass
class SphericalCoordinateLight(BlenderLight):
    azimuth: float = 0
    elevation: float = 45
    theta: float = 0
    distance: float = 1

    def __post_init__(self):
        x, y, z = utils.spherical_to_cartesian(float(self.distance), float(self.azimuth), float(self.elevation))
        q1 = utils.camPosToQuaternion(x, y, z)
        q2 = utils.camRotQuaternion(x, y, z, float(self.theta))
        self.quaternion = utils.quaternionProduct(q2, q1)
        self.xyz = x, y, z
