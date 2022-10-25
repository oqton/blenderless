from blenderless import Blenderless


def test_render(mesh_paths, tmp_path, num_rendering_threads):
    render_path = Blenderless.render(mesh_paths[0], tmp_path, num_threads=num_rendering_threads)
    assert render_path.exists()


def test_gif(mesh_paths, tmp_path, num_rendering_threads):
    dest_path = tmp_path / 'out.gif'
    gif_path = Blenderless.gif(mesh_paths[0], dest_path, frames=5, num_threads=num_rendering_threads)
    assert dest_path.exists()
    assert gif_path == dest_path
