import concurrent.futures
import logging
import multiprocessing
import pathlib
import tempfile

import bpy
import hydra
import imageio.v2 as imageio
from omegaconf import OmegaConf

from blenderless import utils
from blenderless.blender_object import BlenderObject
from blenderless.camera import BlenderCamera
from blenderless.geometry import HorizontalPlane
from blenderless.geometry import Mesh
from blenderless.material import load_materials


def preload_mesh(mesh):
    mesh.load()
    return mesh.mesh


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
                 shadow_plane=False,
                 num_threads=0,
                 verbose: bool | None = None):

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
        self._shadow_plane = shadow_plane
        self._resolution = resolution
        self._num_threads = num_threads
        self._verbose = verbose

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
            images = [imageio.imread(filename) for filename in render_filepaths]
        imageio.mimsave(filepath, images, format='GIF', duration=duration / len(images))
        return filepath

    def _load_scene(self) -> bpy.types.Scene:
        if self._preset_scene is not None:
            scene = [scene for scene in bpy.data.scenes if scene.name == self._preset_scene]
            if not scene:
                raise ValueError(f'scene: {self._preset_scene} not found in preset file: {self._preset_path}')
            bpy.context.window.scene = scene[0]
            self.delete_all_objects()
        else:
            bpy.ops.scene.new(type='EMPTY')

        return bpy.context.scene

    def _preload_meshes(self):
        for obj in self._objects:
            obj.root_dir = self._root_dir
        blender_meshes = [obj for obj in self._objects if isinstance(obj, Mesh)]

        if self._num_threads > 1:
            use_thread_pool = len(blender_meshes) <= 3
            executor_cls = (concurrent.futures.ThreadPoolExecutor if use_thread_pool else multiprocessing.Pool)
            with executor_cls(self._num_threads) as executor:
                meshes = executor.map(preload_mesh, blender_meshes)
        else:
            meshes = [preload_mesh(m) for m in blender_meshes]

        for mesh, blender_mesh in zip(meshes, blender_meshes):
            blender_mesh.mesh = mesh

    def _add_objects(self, blender_scene: bpy.types.Scene):
        for obj in self._objects:  # Add objects to blender.
            blender_scene.collection.children.link(obj.blender_collection())

    def _set_rendering_props(self, blender_scene: bpy.types.Scene):
        blender_scene.render.resolution_x = self._resolution[0]
        blender_scene.render.resolution_y = self._resolution[1]
        blender_scene.render.engine = self._render_engine
        blender_scene.render.film_transparent = self._transparant
        blender_scene.render.image_settings.color_mode = self._color_mode
        if self._num_samples is not None:
            bpy.context.scene.cycles.samples = self._num_samples
        if self._num_threads > 0:
            blender_scene.render.threads = self._num_threads
            blender_scene.render.threads_mode = 'FIXED'

    def _set_cameras(self, blender_scene: bpy.types.Scene):
        # Add default camera when no camera present.
        if len(self.cameras(blender_scene)) == 0:
            camera = BlenderCamera()
            self.add_object(camera)
            blender_scene.collection.children.link(camera.blender_collection())

        # Render for all cameras.
        cameras = self.cameras(blender_scene)
        if len(cameras) == 0:
            raise RuntimeError('No cameras set, fallback default camera did not work.')

        # Set zoom for all cameras.
        for camera in cameras:
            if 'zoomToAll' in camera.data.name:
                blender_scene.camera = camera
                self._zoom_to_all()

        return cameras

    def _print_blender_output(self, output: str, ret_val: list[str]):
        if ((self._verbose is None and logging.root.level == logging.DEBUG) or self._verbose is True or
                ret_val[0] != 'FINISHED'):
            print(output)

    def _render_scene(self, filepath: pathlib.Path, blender_scene: bpy.types.Scene,
                      cameras: list[bpy.types.Camera]) -> list[pathlib.Path]:
        render_files = []
        for n, camera in enumerate(cameras):
            if len(cameras) != 1:
                render_file = filepath.parent / f'{n:03d}_{filepath.name}'
            else:
                render_file = filepath
            blender_scene.render.filepath = str(render_file)
            blender_scene.camera = camera

            with tempfile.TemporaryFile() as fp, utils.stdout_redirected(fp):
                caught_exception = None
                try:
                    ret_val = list(bpy.ops.render.render(write_still=True))
                except Exception as exc:
                    ret_val = ['EXCEPTION']
                    caught_exception = exc
                finally:
                    fp.seek(0)
                    output = fp.read().decode('utf-8')

            self._print_blender_output(output, ret_val)
            if caught_exception:
                raise caught_exception

            if ret_val[0] != 'FINISHED':
                raise RuntimeError(
                    f'Expected blenderpy render return value to be "FINISHED" not {ret_val[0]} for camera {n}')
            render_files.append(pathlib.Path(bpy.context.scene.render.filepath))

        return render_files

    def render(self, filepath, export_blend_path=None):
        bpy.ops.wm.read_factory_settings(use_empty=True)

        if self._preset_path is not None:
            bpy.ops.wm.open_mainfile(filepath=str((self._root_dir / self._preset_path).absolute()))

        blender_scene = self._load_scene()

        if self._preset_path is not None:
            load_materials(self._root_dir / self._preset_path)

        self._preload_meshes()

        self._add_objects(blender_scene)

        self._set_rendering_props(blender_scene)

        cameras = self._set_cameras(blender_scene)

        if self._shadow_plane:  # Add shadow plane when all objects are in the scene.
            self.add_shadow_plane(blender_scene)

        render_files = self._render_scene(pathlib.Path(filepath), blender_scene, cameras)

        if export_blend_path:
            self.export_blend_file(export_blend_path)

        return render_files

    def add_object(self, blender_object: BlenderObject):
        self._objects.append(blender_object)

    def add_shadow_plane(self, blender_scene):
        # Find lowest point.
        lowest_points = []
        for object in self.get_all_objects(['MESH']):
            lowest_points.append(min([v.co.z for v in object.data.vertices]))
        plane = HorizontalPlane(height=min(lowest_points), is_shadow_catcher=True)
        self.add_object(plane)
        blender_scene.collection.children.link(plane.blender_collection())

    @staticmethod
    def cameras(blender_scene):
        return [obj for obj in blender_scene.objects if obj.type == 'CAMERA']

    @staticmethod
    def _zoom_to_all(max_iter=10, delta_min=5e-3):
        """Zoom to view all objects."""
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.context.scene.objects:
            if obj.type in ['MESH', 'FONT']:
                obj.select_set(True)

        cam = bpy.context.scene.camera
        prev_ortho_scale = cam.data.ortho_scale

        # Work-around for camera_to_view_selected() not including entire scene in frame.
        for _ in range(max_iter):
            bpy.ops.view3d.camera_to_view_selected()
            ortho_scale = cam.data.ortho_scale
            delta = abs(ortho_scale - prev_ortho_scale) / prev_ortho_scale
            if delta < delta_min:  # Stop early if the ortho scale doesn't change.
                break
            prev_ortho_scale = ortho_scale

    @staticmethod
    def export_blend_file(filepath):
        bpy.ops.wm.save_as_mainfile(filepath=str(filepath))

    @staticmethod
    def get_all_objects(object_types):
        # Select all objects in the scene to be deleted:
        return [o for o in bpy.context.scene.objects if o.type in object_types]

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
        for o in Scene.get_all_objects(deleteListObjects):
            o.select_set(True)
        bpy.ops.object.delete()

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, verbose: bool):
        self._verbose = verbose
