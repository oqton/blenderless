from dataclasses import dataclass, field

import numpy as np
import trimesh

from blenderless.blender_object import BlenderObject
from blenderless.material import Material, MaterialFromName, add_material


@dataclass
class Geometry(BlenderObject):
    material: Material = MaterialFromName(material_name='Material')
    meta: dict = field(default_factory=dict)

    def blender_object(self, bpy):
        if self._blender_object is None:
            self._blender_object = bpy.data.objects.new(name=self.name, object_data=self.object_data(bpy))
        self._blender_object.location = self.xyz
        self._blender_object.rotation_mode = 'QUATERNION'
        self._blender_object.rotation_quaternion = self.quaternion

        add_material(self._blender_object, self.material.blender_material(bpy))
        return self._blender_object


@dataclass
class Mesh(Geometry):
    mesh_path: str = None
    mesh: trimesh.Trimesh = None
    transformation: np.ndarray = field(default_factory=lambda: np.identity(4))

    def object_data(self, bpy):
        if self._object_data is None:
            self._object_data = bpy.data.meshes.new(name=self.name)
            if self.mesh_path is not None:
                self.mesh = trimesh.load(self.root_dir / self.mesh_path)
            self._object_data.from_pydata(self.mesh.vertices.tolist(), [], self.mesh.faces.tolist())
        return self._object_data


@dataclass
class BlenderLabel(Geometry):
    label_value: str = ''
    size: float = 1.0
    outline_size: float = 0.0
    outline_material: Material = MaterialFromName(material_name='Material')

    def blender_objects(self, bpy):
        objects = []
        bpy.ops.object.text_add()
        text_inside = bpy.data.objects.values()[-1]
        text_inside.data.align_x = 'CENTER'
        text_inside.data.align_y = 'CENTER'
        text_inside.data.body = self.label_value
        text_inside.data.size = self.size
        text_inside.location = self.xyz

        add_material(text_inside, self.material.blender_material(bpy))
        objects.append(text_inside)
        if self.outline_size > 0:
            # add outline
            text_outline = duplicate_object(text_inside)
            text_outline.data.bevel_depth = self.size * self.outline_size
            text_outline.data.fill_mode = 'NONE'
            add_material(text_outline, self.outline_material.blender_material(bpy))
            bpy.context.scene.collection.objects.link(text_outline)
            objects.append(text_outline)

        # remove from current scene
        for obj in objects:
            bpy.context.scene.collection.objects.unlink(obj)

        return objects

    def blender_collection(self, bpy):
        if self._blender_collection is None:
            self._blender_collection = bpy.data.collections.new(self.name)
            for obj in self.blender_objects(bpy):
                self._blender_collection.objects.link(obj)
        return self._blender_collection


def duplicate_object(source_object):
    new_object = source_object.copy()
    new_object.data = source_object.data.copy()
    return new_object
