import multiprocessing
import pathlib
import tempfile
from collections import defaultdict

import bpy
import hydra
import imageio.v2 as imageio
from omegaconf import OmegaConf

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
        self._shadow_plane = shadow_plane
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
            for filenames in render_filepaths.values():
                images.append(imageio.imread(filenames[0]))
        imageio.mimsave(filepath, images, format='GIF', duration=duration / len(images))
        return filepath

    def render(self, output_path, export_blend_path=None, animation=False):
        output_path = pathlib.Path(output_path)
        blender_scene = self.configure_blender_scene(export_blend_path)

        num_frames = self.num_keyframes if animation else 1

        render_files = defaultdict(list)
        cameras = self.cameras(blender_scene)
        for frame_idx in range(num_frames):
            bpy.context.scene.frame_current = frame_idx
            # Set zoom
            for n, camera in enumerate(cameras):
                if 'zoomToAll' in camera.data.name:
                    blender_scene.camera = camera
                    self._zoom_to_all()
                if len(cameras) != 1:
                    render_file = output_path / camera.name / f'{frame_idx}.png'
                else:
                    render_file = output_path / f'{frame_idx}.png'
                blender_scene.render.filepath = str(render_file)
                blender_scene.camera = camera
                if not render_file.parent.exists():
                    render_file.parent.mkdir(parents=True)
                ret_val = list(bpy.ops.render.render(write_still=True))
                if ret_val[0] != 'FINISHED':
                    raise RuntimeError(
                        f'Expected blenderpy render return value to be "FINISHED" not {ret_val[0]} for camera {n}')
                render_files[camera.name].append(pathlib.Path(bpy.context.scene.render.filepath))
        if len(render_files) == 1:
            return list(render_files.values())[0]
        return render_files

    def configure_blender_scene(self, export_blend_path):
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

        # Preload meshes.
        for obj in self._objects:
            obj.root_dir = self._root_dir
        blender_meshes = [obj for obj in self._objects if isinstance(obj, Mesh)]

        if self._num_threads > 1:
            with multiprocessing.Pool(self._num_threads) as p:
                meshes = p.map(preload_mesh, blender_meshes)
        else:
            meshes = [preload_mesh(m) for m in blender_meshes]

        for mesh, blender_mesh in zip(meshes, blender_meshes):
            blender_mesh.mesh = mesh

        # Add objects to blender.
        for obj in self._objects:
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

        # Add shadow plane when all objects are in the scene.
        if self._shadow_plane:
            self.add_shadow_plane(blender_scene)
        if export_blend_path:
            if not export_blend_path.parent.exists():
                export_blend_path.parent.mkdir(parents=True)
            self.export_blend_file(export_blend_path)
        return blender_scene

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

    @property
    def num_keyframes(self):
        return max([len(obj.keyframe_transformations) for obj in self._objects if isinstance(obj, BlenderObject)])

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
