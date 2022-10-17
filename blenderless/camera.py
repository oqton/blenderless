from dataclasses import dataclass
from dataclasses import field

import bpy

from blenderless import utils
from blenderless.blender_object import BlenderObject


@dataclass
class BlenderCamera(BlenderObject):
    camera_type: str = 'ORTHO'
    clipping_distance: float = 5000
    zoom_to_all: bool = field(default=True)

    def object_data(self):
        if self._object_data is None:
            self._object_data = bpy.data.cameras.new(name=self.name)
            self._object_data.type = self.camera_type
            self._object_data.clip_end = self.clipping_distance
            if self.zoom_to_all:
                self._object_data.name += 'zoomToAll'
        return self._object_data


@dataclass
class SphericalCoordinateCamera(BlenderCamera):
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
