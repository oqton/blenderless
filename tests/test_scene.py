import pytest
from PIL import Image

from blenderless.camera import BlenderCamera
from blenderless.scene import Scene


@pytest.fixture(name='new_scene')
def new_scene(num_rendering_threads):
    return Scene(num_threads=num_rendering_threads)


def test_render_empty_scene(new_scene, tmp_path):
    render_path = tmp_path / 'out.png'
    new_scene.render(render_path)
    assert render_path.exists()


def test_render_multiple_cameras(new_scene, tmp_path):
    num_cameras = 2

    for _ in range(num_cameras):
        new_scene.add_object(BlenderCamera())

    render_filepaths = new_scene.render(tmp_path / 'out.png')

    for path in render_filepaths:
        assert path.exists()
    assert len(render_filepaths) == num_cameras


def test_set_resolution(num_rendering_threads, tmp_path):
    x, y = 25, 50
    render_path = tmp_path / 'out.png'
    scene = Scene(num_threads=num_rendering_threads, resolution=(x, y))
    scene.render(render_path)
    assert render_path.exists()
    im = Image.open(render_path)
    width, height = im.size
    assert x == width
    assert y == height


def test_load_scene_from_config(example_config_path, tmp_path):
    scene = Scene.from_config(example_config_path)
    render_path = tmp_path / 'out.png'
    scene.render(render_path)
    assert render_path.exists()


def test_render_gif(new_scene, tmp_path):
    num_cameras = 2

    for _ in range(num_cameras):
        new_scene.add_object(BlenderCamera())

    gif_path = tmp_path / 'out.gif'
    new_scene.render_gif(gif_path)
    gif_path.exists()
