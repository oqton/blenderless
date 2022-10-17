from abc import abstractmethod
from dataclasses import dataclass
from typing import List

import bpy


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
    _blender_object = None
    _object_data = None

    def blender_object(self):
        if self._blender_object is None:
            # This initializes the blender object and calls object_data() which should be overwritten by child class
            self._blender_object = bpy.data.objects.new(name=self.name, object_data=self.object_data())
        self._blender_object.location = self.xyz
        self._blender_object.rotation_mode = 'QUATERNION'
        self._blender_object.rotation_quaternion = self.quaternion
        return self._blender_object

    @abstractmethod
    def object_data(self):
        pass
