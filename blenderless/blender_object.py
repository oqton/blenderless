from abc import abstractmethod
from dataclasses import dataclass
from typing import List

import bpy
import numpy as np
import trimesh


@dataclass
class BlenderCollection:
    _blender_collection = None

    def blender_collection(self):
        if self._blender_collection is None:
            self._blender_collection = bpy.data.collections.new(self.name)

            # Initialize a single blender object to this collection
            self._blender_collection.objects.link(self.blender_object())
        return self._blender_collection

    @abstractmethod
    def blender_object(self):
        pass

    @abstractmethod
    def object_data(self):
        pass


@dataclass
class BlenderObject(BlenderCollection):
    name: str = ''
    xyz: List[float] = (0, 0, 0)
    quaternion: List[float] = (1, 0, 0, 0)
    keyframe_transformations: List[np.ndarray] = ()
    _blender_object = None
    _object_data = None

    def blender_object(self):
        if self._blender_object is None:
            # This initializes the blender object and calls object_data() which should be overwritten by child class
            self._blender_object = bpy.data.objects.new(name=self.name, object_data=self.object_data())
        self._blender_object.location = self.xyz
        self._blender_object.rotation_mode = 'QUATERNION'
        self._blender_object.rotation_quaternion = self.quaternion
        if self.keyframe_transformations:
            for frame_idx, transformation in enumerate(self.keyframe_transformations):
                scale, shear, angles, translate, perspective = trimesh.transformations.decompose_matrix(transformation)
                self._blender_object.location = translate
                self._blender_object.scale = scale
                self._blender_object.rotation_quaternion = trimesh.transformations.quaternion_from_euler(*angles)
                self._blender_object.keyframe_insert(data_path='location', frame=frame_idx)
                self._blender_object.keyframe_insert(data_path='scale', frame=frame_idx)
                self._blender_object.keyframe_insert(data_path='rotation_quaternion', frame=frame_idx)
        return self._blender_object

    @abstractmethod
    def object_data(self):
        pass
