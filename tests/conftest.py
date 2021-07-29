import pathlib

import pytest


@pytest.fixture
def test_data_path():
    return pathlib.Path(__file__).parent / 'test_data'


@pytest.fixture
def mesh_paths(test_data_path):
    return list((test_data_path / 'mesh').glob('*'))


@pytest.fixture
def example_config_path(test_data_path):
    return test_data_path / 'configs' / 'simple' / 'scene.yaml'
