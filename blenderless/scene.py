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
                 preset_scene=None,
                 render_engine='CYCLES',
                 num_samples=None,
                 transparant=True,
                 color_mode='RGBA',
                 resolution=(512, 512),
                 num_threads=0):

        self._objects = []
        self._root_dir = root_dir
        if self._root_dir is None:
            self._root_dir = pathlib.Path()
        self._preset_path = preset_path
        self._preset_scene = preset_scene
        self._render_engine = render_engine
        self._num_samples = num_samples
        self._transparant = transparant
        self._color_mode = color_mode
        self._resolution = resolution
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

        bpy.ops.wm.read_factory_settings(use_empty=True)
        if self._preset_path is not None and self._preset_scene is not None:
            bpy.ops.wm.open_mainfile(filepath=str((self._root_dir / self._preset_path).absolute()))

            scene = [scene for scene in bpy.data.scenes if scene.name == self._preset_scene]
            if len(scene) == 0:
                raise ValueError(f'scene: {self._preset_scene} not found in preset file: {self._preset_path}')
            bpy.context.window.scene = scene[0]
            self.delete_all_objects()

        else:
            bpy.ops.scene.new(type='EMPTY')
        blender_scene = bpy.context.scene

        if self._preset_path is not None:
            load_materials(self._root_dir / self._preset_path)

        for obj in self._objects:
            obj.root_dir = self._root_dir
            blender_scene.collection.children.link(obj.blender_collection())

        # Set rendering properties.
        if self._num_samples is not None:
            bpy.context.scene.cycles.samples = self._num_samples
        blender_scene.render.resolution_x = self._resolution[0]
        blender_scene.render.resolution_y = self._resolution[1]
        blender_scene.render.engine = self._render_engine
        blender_scene.render.film_transparent = self._transparant
        blender_scene.render.image_settings.color_mode = self._color_mode
        if self._num_threads > 0:
            blender_scene.render.threads = self._num_threads
            blender_scene.render.threads_mode = 'FIXED'

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
            blender_scene.render.filepath = str(render_file)

            blender_scene.camera = camera
            if 'zoomToAll' in camera.data.name:
                self._zoom_to_all()
            ret_val = list(bpy.ops.render.render(write_still=True))
            if ret_val[0] != 'FINISHED':
                raise RuntimeError(
                    f'Expected blenderpy render return value to be "FINISHED" not {ret_val[0]} for camera {n}')
            render_files.append(pathlib.Path(bpy.context.scene.render.filepath))

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

    @staticmethod
    def delete_all_objects():
        """
        Deletes all objects in the current scene
        """
        deleteListObjects = [
            'MESH', 'CURVE', 'META', 'FONT', 'HAIR', 'POINTCLOUD', 'VOLUME', 'GPENCIL', 'ARMATURE', 'LATTICE',
            'LIGHT_PROBE', 'CAMERA', 'SPEAKER'
        ]

        bpy.ops.object.select_all(action='DESELECT')
        # Select all objects in the scene to be deleted:
        for o in bpy.context.scene.objects:
            if o.type in deleteListObjects:
                o.select_set(True)
            else:
                o.select_set(False)
        bpy.ops.object.delete()
