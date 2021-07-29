import pathlib
from dataclasses import dataclass
from typing import List

DEFAULT_MATERIAL_PATH = pathlib.Path(__file__).parent / 'data/materials.blend'


def load_default_materials(bpy):
    load_materials(bpy, DEFAULT_MATERIAL_PATH)


def load_materials(bpy, filepath):
    with bpy.data.libraries.load(str(filepath.absolute())) as (data_from, data_to):
        data_to.materials = data_from.materials


@dataclass
class Material:
    name: str = ''
    _blender_material = None


@dataclass
class MaterialRGBA(Material):
    rgba: List[float] = (0, 0, 255, 255)  # default color blue

    def blender_material(self, bpy):
        if self._blender_material is None:
            self._blender_material = bpy.data.materials.new(name=self.name)
            self._blender_material.diffuse_color = self.rgba
        return self._blender_material


@dataclass
@dataclass
class MaterialFromName(Material):
    material_name: str = ''
    _blender_material = None

    def blender_material(self, bpy):
        if self._blender_material is None:
            self._blender_material = bpy.data.materials[self.material_name]
        return self._blender_material


def add_material(blender_object, blender_material):
    blender_object.data.materials.clear()
    blender_object.data.materials.append(blender_material)
