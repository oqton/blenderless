from blenderless.material import MaterialFromName, MaterialRGBA


def test_create_material_from_name():
    material_name = 'Material'
    material = MaterialFromName(material_name=material_name)


def test_create_material_rgba():
    rgba = [255., 0., 0., 255.]
    material = MaterialRGBA(rgba=rgba)
