import pathlib
import tempfile

import trimesh

from blenderless.geometry import BlenderLabel, Mesh
from blenderless.material import MaterialRGBA
from blenderless.scene import Scene


def test_render_mesh(mesh_paths):
    for mesh_path in mesh_paths:
        scene = Scene()

        blender_mesh = Mesh(name='foo_mesh', mesh=trimesh.load(mesh_path))
        scene.add_object(blender_mesh)
        with tempfile.TemporaryDirectory() as tmpdirname:
            render_path = tmpdirname / pathlib.Path('render.png')
            scene.render(render_path)
            assert render_path.exists()


def test_render_label():
    scene = Scene()
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
