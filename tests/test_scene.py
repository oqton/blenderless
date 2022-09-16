from PIL import Image

from blenderless.camera import BlenderCamera
from blenderless.scene import Scene


def test_create_new_scene():
    scene = Scene()


def test_render_empty_scene(tmp_path):
    scene = Scene()
    render_path = tmp_path / 'out.png'
    scene.render(render_path, num_threads=8)
    assert render_path.exists()


def test_render_multiple_cameras(tmp_path):
    num_cameras = 2

    scene = Scene()
    for _ in range(num_cameras):
        scene.add_object(BlenderCamera())

    render_filepaths = scene.render(tmp_path / 'out.png', num_threads=8)

    for path in render_filepaths:
        assert path.exists()
    assert len(render_filepaths) == num_cameras


def test_set_resolution(tmp_path):
    x, y = 25, 50
    scene = Scene()
    render_path = tmp_path / 'out.png'
    scene.render(render_path, resolution=(x, y), num_threads=8)
    assert render_path.exists()
    im = Image.open(render_path)
    width, height = im.size
    assert x == width
    assert y == height


def test_load_scene_from_config(example_config_path, tmp_path):
    scene = Scene.from_config(example_config_path)
    render_path = tmp_path / 'out.png'
    scene.render(render_path, num_threads=8)
    assert render_path.exists()


def test_render_gif(tmp_path):
    num_cameras = 2

    scene = Scene()
    for _ in range(num_cameras):
        scene.add_object(BlenderCamera())

    gif_path = tmp_path / 'out.gif'
    scene.render_gif(gif_path, num_threads=8)
    gif_path.exists()
