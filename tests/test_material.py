import numpy as np
import numpy.testing as npt

from blenderless.material import MaterialFromName, MaterialRGBA


def test_create_material_from_name():
    material_name = 'Material'
    material = MaterialFromName(material_name=material_name)
    assert material.material_name == material_name


def test_create_material_rgba():
    rgba = [255., 0., 0., 255.]
    material = MaterialRGBA(rgba=rgba)
    npt.assert_allclose(material.rgba, rgba)


def test_material_from_colormap():
    # Without alphas
    colormap = np.array([[128, 0, 0], [0, 128, 0]])
    matlist = MaterialRGBA.material_list_from_colormap(colormap)

    for i, rgbamat in enumerate(matlist):
        assert isinstance(rgbamat, MaterialRGBA)
        npt.assert_allclose(rgbamat.rgba[:3], colormap[i, :])
        assert rgbamat.material_name == f'label{i}'

    # With alphas
    colormap = np.array([[128, 0, 0, 255], [0, 128, 0, 128]])
    matlist = MaterialRGBA.material_list_from_colormap(colormap)

    for i, rgbamat in enumerate(matlist):
        assert isinstance(rgbamat, MaterialRGBA)
        npt.assert_allclose(rgbamat.rgba, colormap[i, :])
