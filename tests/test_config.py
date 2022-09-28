import os
import pathlib

import numpy as np
import pytest
from PIL import Image
from skimage.metrics import structural_similarity

from blenderless.scene import Scene


def examples():
    return pathlib.Path('tests/test_data/configs').glob('*')


@pytest.mark.parametrize("example_path", examples())
def test_load_scene_from_config(example_path, test_outputs_dir):
    outputs_dir = test_outputs_dir / os.path.basename(example_path)
    os.makedirs(outputs_dir)

    test_output_filepath = outputs_dir / 'test_output.png'
    test_output_filepath = pathlib.Path(
        '/home/avlaminck/oqton/repos/blenderless/tests/test_data/configs') / outputs_dir.name / 'test_output.png'
    blend_scene_filepath = outputs_dir / 'scene.blend'

    scene = Scene.from_config(example_path / 'scene.yaml')
    render_paths = scene.render(test_output_filepath, export_blend_path=blend_scene_filepath)
    assert test_output_filepath.exists()
    assert render_paths[0] == test_output_filepath

    # compare with reference
    reference_filepath = example_path / 'reference.png'
    assert reference_filepath.exists()

    base_render = np.asarray(Image.open(test_output_filepath))
    test_render = np.asarray(Image.open(reference_filepath))

    assert structural_similarity(base_render, test_render, multichannel=True) > 0.995
