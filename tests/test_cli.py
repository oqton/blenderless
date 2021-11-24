from shutil import copyfile

from click.testing import CliRunner

import blenderless.cli


def test_file_rendering(tmp_path, mesh_paths):
    mesh_path = mesh_paths[0]
    runner = CliRunner()

    copyfile(mesh_path, tmp_path / mesh_path.name)
    result = runner.invoke(blenderless.cli.image, [mesh_path.name, str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / f'{mesh_path.stem}.png').exists()


def test_config_rendering(example_config_path, tmp_path):
    runner = CliRunner()
    output_file = tmp_path / 'render.png'
    result = runner.invoke(blenderless.cli.config, [str(example_config_path), str(output_file)])
    assert result.exit_code == 0
    assert output_file.exists()


def test_export_blender_path(example_config_path, tmp_path):
    runner = CliRunner()
    output_file = tmp_path / 'render.png'
    blender_file = tmp_path / 'render.blend'
    result = runner.invoke(
        blenderless.cli.main,
        ['--export-blend-path',
         str(blender_file), 'config',
         str(example_config_path),
         str(output_file)])
    assert result.exit_code == 0
    assert output_file.exists()
    assert blender_file.exists()
