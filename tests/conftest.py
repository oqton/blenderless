import os
import pathlib

import pytest


@pytest.fixture
def test_data_path():
    return pathlib.Path('tests/test_data')


@pytest.fixture
def mesh_paths(test_data_path):
    return list((test_data_path / 'mesh').glob('*'))


@pytest.fixture
def example_config_path(test_data_path):
    return test_data_path / 'configs' / 'simple' / 'scene.yaml'


@pytest.fixture
def num_rendering_threads():
    return 1


@pytest.fixture
def test_outputs_dir() -> pathlib.Path:
    return pathlib.Path(os.getenv('TEST_UNDECLARED_OUTPUTS_DIR', ''))
