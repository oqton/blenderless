import blenderless


def test_render(mesh_paths, tmp_path):
    dest_path = tmp_path / 'out.png'
    render_path = blenderless.render(mesh_paths[0], dest_path)
    assert dest_path.exists()
    assert render_path == dest_path


def test_gif(mesh_paths, tmp_path):
    dest_path = tmp_path / 'out.gif'
    gif_path = blenderless.gif(mesh_paths[0], dest_path, frames=5)
    assert dest_path.exists()
    assert gif_path == dest_path
