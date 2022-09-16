import os
import pathlib
import tempfile

import bpy
import hydra
import imageio
from omegaconf import OmegaConf

from blenderless.blender_object import BlenderObject
from blenderless.camera import BlenderCamera
from blenderless.material import load_materials


class Scene:

    def __init__(self,
                 root_dir=None,
                 preset_path=None,
                 render_engine='CYCLES',
                 transparant=True,
                 color_mode='RGBA',
                 resolution=(512, 512),
                 light='MATCAP',
                 studio_light='check_rim_dark.exr',
                 num_threads=0):
        self._objects = []
        self._root_dir = root_dir
        if self._root_dir is None:
            self._root_dir = pathlib.Path()
        self._preset_path = preset_path

        self._render_engine = render_engine
        self._transparant = transparant
        self._color_mode = color_mode
        self._resolution = resolution
        self._light = light
        self._studio_light = studio_light
        self._num_threads = num_threads

    @classmethod
    def from_config(cls, config_path, root_dir=None):
        config = OmegaConf.load(config_path)

        if root_dir is None:
            root_dir = pathlib.Path(config_path).parent
        else:
            root_dir = pathlib.Path(root_dir)
        scene = hydra.utils.instantiate(config.scene, _target_=cls, root_dir=root_dir)

        for camera in config.cameras:
            scene.add_object(hydra.utils.instantiate(camera))

        for obj in config.objects:
            scene.add_object(hydra.utils.instantiate(obj))

        return scene

    def render_gif(self, filepath, duration=2, **kwargs):
        with tempfile.TemporaryDirectory() as tmpdirname:
            render_path = pathlib.Path(tmpdirname) / 'out.png'
            render_filepaths = self.render(render_path, **kwargs)
            images = []
            for filename in render_filepaths:
                images.append(imageio.imread(filename))
        imageio.mimsave(filepath, images, format='GIF', duration=duration / len(images))
        return filepath

    def render(self, filepath, export_blend_path=None):
        filepath = pathlib.Path(filepath)
        bpy.ops.scene.new(type='EMPTY')
        blender_scene = bpy.context.scene

        if self._preset_path is not None:
            load_materials(self._root_dir / self._preset_path)

        for obj in self._objects:
            obj.root_dir = self._root_dir
            blender_scene.collection.children.link(obj.blender_collection())

        # Set rendering properties.
        blender_scene.render.resolution_x = self._resolution[0]
        blender_scene.render.resolution_y = self._resolution[1]
        blender_scene.render.engine = self._render_engine
        blender_scene.render.film_transparent = self._transparant
        blender_scene.render.image_settings.color_mode = self._color_mode
        if self._num_threads > 0:
            blender_scene.render.threads = self._num_threads
            blender_scene.render.threads_mode = 'FIXED'

        # Set lighting mode.
        blender_scene.display.shading.light = self._light
        blender_scene.display.shading.studio_light = self._studio_light

        # Add default camera when no camera present.
        if len(self.cameras(blender_scene)) == 0:
            camera = BlenderCamera()
            self.add_object(camera)
            blender_scene.collection.children.link(camera.blender_collection())

        # Render for all cameras.
        cameras = self.cameras(blender_scene)
        if len(cameras) == 0:
            raise RuntimeError('No cameras set, fallback default camera did not work.')

        render_files = []
        for n, camera in enumerate(cameras):
            if len(cameras) != 1:
                render_file = filepath.parent / f'{n:03d}_{filepath.name}'
            else:
                render_file = filepath

            render_files.append(render_file)
            blender_scene.render.filepath = str(render_file)

            blender_scene.camera = camera
            if 'zoomToAll' in camera.data.name:
                self._zoom_to_all()
            ret_val = list(bpy.ops.render.render(write_still=True))
            if ret_val[0] != 'FINISHED':
                raise RuntimeError(
                    f'Expected blenderpy render return value to be "FINISHED" not {ret_val[0]} for camera {n}')

        if export_blend_path:
            self.export_blend_file(export_blend_path)
        return render_files

    def add_object(self, blender_object: BlenderObject):
        self._objects.append(blender_object)

    @staticmethod
    def cameras(blender_scene):
        return [obj for obj in blender_scene.objects if obj.type == 'CAMERA']

    @staticmethod
    def _zoom_to_all():
        """Zoom to view all objects."""
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH' or obj.type == 'FONT':
                obj.select_set(True)
        bpy.ops.view3d.camera_to_view_selected()

    @staticmethod
    def export_blend_file(filepath):
        bpy.ops.wm.save_as_mainfile(filepath=str(filepath))
