from dataclasses import dataclass, field
from typing import List

import numpy as np
import trimesh

from blenderless.blender_object import BlenderObject
from blenderless.material import Material, MaterialFromName, MaterialRGBA, add_material


@dataclass
class Geometry(BlenderObject):
    """Geometry Blender Object.

    This class allows a material to be added to the object.
    """
    material: Material = MaterialFromName(material_name='Material')
    material_list: List[Material] = None
    colormap: np.ndarray = None
    meta: dict = field(default_factory=dict)
    labels: np.ndarray = None

    def blender_object(self, bpy):
        super().blender_object(bpy)
        if self.colormap is not None:
            self.material_list = MaterialRGBA.material_list_from_colormap(self.colormap)

        if self.material_list:
            for material in self.material_list:
                add_material(self._blender_object, material.blender_material(bpy))
        else:
            add_material(self._blender_object, self.material.blender_material(bpy))

        return self._blender_object

    def _set_face_material_indices(self):
        """Should be run at the end of object_data() if labeling is desired."""
        if self.labels is not None:
            # Map each face to a material depending on their label
            # Note that materials are not loaded yet as object_data() is executed during the construction
            # blender_object(). Labels that are greater than the largest material index, will receive the
            # last material index.
            for f in self._object_data.polygons:
                f.material_index = self.labels[f.index]  # material slot index


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
            verts = trimesh.transformations.transform_points(self.mesh.vertices, self.transformation)
            self._object_data.from_pydata(verts.tolist(), [], self.mesh.faces.tolist())
            self._set_face_material_indices()

        return self._object_data


@dataclass
class PointCloud(Geometry):
    """PointCloud representation.

    Point cloud support is currently flakey in blender. Therefore, point clouds are converted into a mesh object
    by placing an octahedron around each point (6 faces, 8 points).

    There is a bpy.data.pointclouds class, which is possible to instantiate. However,
    there is no way of populating the points attribute as it is read-only. Other options are
    to use ther particle representation, however, for the application of this library, it is
    easier if the point cloud is converted into a mesh object.
    """
    points: np.ndarray = None
    point_size: float = 0.3
    transformation: np.ndarray = field(default_factory=lambda: np.identity(4))

    def object_data(self, bpy):
        if self._object_data is None:
            self._object_data = bpy.data.meshes.new(name=self.name)

            points = trimesh.transformations.transform_points(self.points, self.transformation)

            # Convert to octahedrons and repeat corresponding labels 8 times.
            verts, faces = self._convert_points_to_octahedrons(points, self.point_size)
            if self.labels is not None:
                self.labels = np.repeat(self.labels, 8, axis=0)

            self._object_data.from_pydata(verts.tolist(), [], faces.tolist())
            self._set_face_material_indices()

        return self._object_data

    @staticmethod
    def _convert_points_to_octahedrons(points, point_size=0.3):
        """Return vertices and faces for octahedrons centered around the given points."""

        n_points = points.shape[0]
        offsets = [[-1., 0., 0.], [0., 1., 0.], [1., 0., 0.], [0., -1., 0.]]  # Z = 0
        offsets += [[0., 0., 1.], [0., 0., -1.0]]
        offsets = np.array(offsets) * point_size / 2

        vertices = np.repeat(points, 6, axis=0)
        vertices = vertices + np.tile(offsets, (n_points, 1))

        faces_base = [[0, 1, 4], [1, 2, 4], [2, 3, 4], [0, 3, 4], [0, 1, 5], [1, 2, 5], [2, 3, 5], [0, 3, 5]]
        faces = np.tile(faces_base, [n_points, 1]) + np.repeat(np.arange(n_points) * 6, 8)[:, None]
        return vertices, faces


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
