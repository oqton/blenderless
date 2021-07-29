import blenderless


def test_render(mesh_paths, tmp_path):
    dest_path = tmp_path / 'out.png'
    render_paths = blenderless.render(mesh_paths[0], dest_path)
    assert dest_path.exists()
