import pathlib
import tempfile
from multiprocessing import Process, Queue

import hydra
import imageio
from omegaconf import OmegaConf
from xvfbwrapper import Xvfb

from blenderless.blender_object import BlenderObject
from blenderless.camera import BlenderCamera
from blenderless.material import load_materials


def import_bpy():
    """Import blenderpy.

    The reason for this late-loading is that communication with Blender is
    restricted to a single separate render thread.
    """
    import bpy
    return bpy


class Scene():

    #pylint: disable=too-many-arguments
    def __init__(self,
                 render_engine='BLENDER_WORKBENCH',
                 transparant=True,
                 color_mode='RGBA',
                 resolution=(512, 512),
                 zoom_to_all=True,
                 preset_path=None,
                 light='MATCAP',
                 studio_light='check_rim_dark.exr',
                 root_dir=pathlib.Path('.')):

        self._objects = []
        self.render_engine = render_engine
        self.transparant = transparant
        self.color_mode = color_mode
        self.resolution = resolution
        self.zoom_to_all = zoom_to_all
        self.preset_path = preset_path
        self.light = light
        self.studio_light = studio_light
        self.root_dir = root_dir

    @classmethod
    def from_config(cls, config_path, root_dir=None):
        config = OmegaConf.load(config_path)

        if root_dir is None:
            root_dir = pathlib.Path(config_path).parent
        else:
            root_dir = pathlib.Path(root_dir)
        scene = hydra.utils.instantiate(config.scene, _target_=cls, root_dir=root_dir)

        # load cameras
        for camera in config.cameras:
            scene.add_object(hydra.utils.instantiate(camera))

        # load objects
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
        filepath_queue = Queue()
        if isinstance(filepath, str):
            filepath = pathlib.PosixPath(filepath)
        p = Process(target=self._render, args=(self, filepath, export_blend_path, filepath_queue))
        p.start()
        p.join()
        filepath_list = []
        while not filepath_queue.empty():
            filepath_list.append(filepath_queue.get())
        return filepath_list

    @staticmethod
    def _render(self, filepath, export_blend_path, filepath_queue):
        with Xvfb():
            filepath = pathlib.Path(filepath)
            bpy = import_bpy()
            bpy.ops.scene.new(type='EMPTY')
            blender_scene = bpy.context.scene

            # load materials
            if self.preset_path:
                load_materials(bpy, self.root_dir / self.preset_path)

            for obj in self._objects:
                obj.root_dir = self.root_dir
                blender_scene.collection.children.link(obj.blender_collection(bpy))

            # set render properties
            blender_scene.render.resolution_x = self.resolution[0]
            blender_scene.render.resolution_y = self.resolution[1]
            blender_scene.render.engine = self.render_engine
            blender_scene.render.film_transparent = self.transparant
            blender_scene.render.image_settings.color_mode = self.color_mode

            # set lighting mode
            if self.light:
                blender_scene.display.shading.light = self.light
            if self.studio_light:
                blender_scene.display.shading.studio_light = self.studio_light

            # add default camera when no camera present
            if len(self.cameras(blender_scene)) == 0:
                camera = BlenderCamera()
                self.add_object(camera)
                blender_scene.collection.children.link(camera.blender_collection(bpy))

            # render for all cameras
            cameras = self.cameras(blender_scene)
            for n, camera in enumerate(cameras):
                if len(cameras) != 1:
                    render_file = filepath.parent / f'{n:03d}_{filepath.name}'
                else:
                    render_file = filepath

                filepath_queue.put(render_file)
                blender_scene.render.filepath = str(render_file)

                blender_scene.camera = camera
                if self.zoom_to_all:
                    self._zoom_to_all(bpy)
                bpy.ops.render.render(write_still=True)

            if export_blend_path:
                self.export_blend_file(bpy, export_blend_path)

    def add_object(self, blender_object: BlenderObject):
        self._objects.append(blender_object)

    @staticmethod
    def cameras(blender_scene):
        return [obj for obj in blender_scene.objects if obj.type == 'CAMERA']

    @staticmethod
    def _zoom_to_all(bpy):
        # zoom to view all objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH' or obj.type == 'FONT':
                obj.select_set(True)
        bpy.ops.view3d.camera_to_view_selected()

    @staticmethod
    def export_blend_file(bpy, filepath):
        bpy.ops.wm.save_as_mainfile(filepath=str(filepath))
