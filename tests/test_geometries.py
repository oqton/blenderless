import pathlib
import tempfile
from unittest.mock import MagicMock

import numpy as np
import numpy.testing as npt
import trimesh

from blenderless.geometry import BlenderLabel, Geometry, Mesh, PointCloud
from blenderless.material import MaterialRGBA
from blenderless.scene import Scene


def test_render_mesh(mesh_paths, num_rendering_threads):
    for mesh_path in mesh_paths:
        scene = Scene(num_threads=num_rendering_threads)

        blender_mesh = Mesh(name='foo_mesh', mesh=trimesh.load(mesh_path))
        scene.add_object(blender_mesh)
        with tempfile.TemporaryDirectory() as tmpdirname:
            render_path = tmpdirname / pathlib.Path('render.png')
            scene.render(render_path)
            assert render_path.exists()


# TODO(axelvlaminck) Please fix this.
# def test_render_transformation():
#     verts = np.eye(3, dtype=np.float32)
#     faces = np.array([[0, 1, 2]])
#     transformation = np.diag([2., 3., 4., 1.])
#     transformation[0, 3] = 1.

#     t_mesh = trimesh.Trimesh(vertices=verts, faces=faces)

#     # Use MagicMock to avoid loading bpy, makes test slightly overcomplicated
#     bpy = MagicMock()
#     bpy.data.meshes.new.ret_val = None
#     b_mesh = Mesh(mesh=t_mesh, transformation=transformation)
#     b_mesh.object_data()

#     gt_verts = np.array([[3., 0., 0.], [1., 3., 0.], [1., 0., 4.]])

#     # Instrument how the vertices are passed to bpy
#     called_verts = b_mesh._object_data.from_pydata.call_args[0][0]

#     npt.assert_allclose(gt_verts, called_verts)


def test_render_label(num_rendering_threads):
    scene = Scene(num_threads=num_rendering_threads)
    red_material = MaterialRGBA(rgba=(128, 0, 0, 1))
    yellow_material = MaterialRGBA(rgba=(128, 128, 0, 1))
    blender_label = BlenderLabel(label_value='test',
                                 outline_size=0.01,
                                 material=red_material,
                                 outline_material=yellow_material)
    scene.add_object(blender_label)
    with tempfile.TemporaryDirectory() as tmpdirname:
        render_path = tmpdirname / pathlib.Path('render.png')
        scene.render(render_path)
        assert render_path.exists()


def test_convert_points_to_octahedrons():
    points = np.array([[0., 0., 0.], [1., 1., 1.]])
    verts, faces = PointCloud._convert_points_to_octahedrons(points, point_size=0.7)

    exp_verts = np.array([[-0.35, 0., 0.], [0., 0.35, 0.], [0.35, 0., 0.], [0., -0.35, 0.], [0., 0., 0.35],
                          [0., 0., -0.35], [0.65, 1., 1.], [1., 1.35, 1.], [1.35, 1., 1.], [1., 0.65, 1.],
                          [1., 1., 1.35], [1., 1., 0.65]])

    exp_faces = np.array([[0, 1, 4], [1, 2, 4], [2, 3, 4], [0, 3, 4], [0, 1, 5], [1, 2, 5], [2, 3, 5], [0, 3, 5],
                          [6, 7, 10], [7, 8, 10], [8, 9, 10], [6, 9, 10], [6, 7, 11], [7, 8, 11], [8, 9, 11],
                          [6, 9, 11]])

    # Check if meshes are watertight
    mesh = trimesh.Trimesh(vertices=verts, faces=faces)
    assert mesh.is_watertight

    npt.assert_allclose(verts, exp_verts)
    npt.assert_allclose(faces, exp_faces)


def test_set_face_material_indices():
    obj = MagicMock()
    obj.labels = [0, 1, 0, 1, 0]
    obj._object_data = MagicMock()
    obj._object_data.polygons = []
    for i in range(5):
        m = MagicMock()
        m.index = i
        obj._object_data.polygons.append(m)

    Geometry._set_face_material_indices(obj)

    for i in range(5):
        assert obj._object_data.polygons[i].material_index == obj.labels[i]
