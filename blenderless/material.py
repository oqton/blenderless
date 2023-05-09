import pathlib
from dataclasses import dataclass
from typing import List
from typing import Optional

import bpy
import numpy as np

DEFAULT_MATERIAL_PATH = pathlib.Path(__file__).parent / 'data/materials.blend'


def load_default_materials():
    load_materials(DEFAULT_MATERIAL_PATH)


def load_materials(filepath):
    """Load materials from materials file.

    Use the MaterialFromName class to load materials from this file.
    """

    existing_material_names = [m.name for m in bpy.data.materials]

    with bpy.data.libraries.load(str(filepath.absolute())) as (data_from, data_to):
        # Loading the same material twice causes a seg fault in blender.
        for name in filter(lambda n: n not in existing_material_names, data_from.materials):
            data_to.materials.append(name)


def convert_to_linear_colorspace(c):
    if c < 0:
        return 0
    elif c < 0.04045:
        return c / 12.92
    else:
        return ((c + 0.055) / 1.055)**2.4


def srgba_to_linearrgba(srgba):
    return [convert_to_linear_colorspace(c) for c in srgba[:3]] + [srgba[3]]


@dataclass
class Material:
    """Material base class."""
    material_name: str = ''
    _blender_material = None


@dataclass
class MaterialRGBA(Material):
    """Create diffuse single color material."""
    rgba: List[float] = (0.8, 0.8, 0.8, 1)  # default color white

    def blender_material(self):
        if self._blender_material is None:
            self._blender_material = bpy.data.materials.new(name=self.material_name)
            self._blender_material.diffuse_color = self.rgba
        return self._blender_material

    @staticmethod
    def material_list_from_colormap(colormap: np.ndarray) -> List[Material]:
        """Create list of materials based on colormap.

        Args:
            colormap (np.ndarray): row-wise colors, Shape (?, 3) or (?, 4)
        """
        n, d = colormap.shape
        if d == 3:
            colormap = np.concatenate((colormap, np.ones((n, 1))), axis=1)

        materials = [None] * n
        for i in range(n):
            materials[i] = MaterialRGBA(rgba=tuple(colormap[i, :]), material_name=f'label{i}')
        return materials


@dataclass
class MaterialFromName(Material):
    """Material loader using string identifier.

    Load material from preset file, see load_materials().
    """
    rgba: Optional[List[float]] = None
    _blender_material = None

    def blender_material(self):
        if self._blender_material is None:
            self._blender_material = bpy.data.materials[self.material_name]
            if self.rgba is not None:
                self._blender_material = self._blender_material.copy()
                for node in self._blender_material.node_tree.nodes:
                    if 'ColorRamp' in node.name:
                        num_elements = len(node.color_ramp.elements)
                        for n in range(num_elements):
                            node.color_ramp.elements[n].color = srgba_to_linearrgba(self.rgba)
                        node.color_ramp.elements[n].color = (0, 0, 0, 1)
        return self._blender_material


def add_material(blender_object, blender_material):
    """Add material to blender object."""
    blender_object.data.materials.clear()
    blender_object.data.materials.append(blender_material)
