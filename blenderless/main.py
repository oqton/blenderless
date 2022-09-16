import pathlib
import tempfile
import uuid
from typing import Optional

from blenderless.camera import SphericalCoordinateCamera
from blenderless.geometry import Mesh
from blenderless.scene import Scene
from blenderless.utils import notebook_preview


class Blenderless():
    """Class to run render pipelines."""

    export_blend_path: Optional[str] = None
    """Path to export the generated .blend file to."""

    @classmethod
    @notebook_preview
    def render(cls, mesh_path, dest_path=None, azimuth=45, elevation=30, theta=0, **kwargs):
        """Render single frame as PNG."""
        if dest_path is None:
            dest_path = pathlib.PosixPath(tempfile.gettempdir()) / f'{uuid.uuid4().int}.png'

        scene = Scene(**kwargs)
        scene.add_object(Mesh(mesh_path=mesh_path))
        scene.add_object(SphericalCoordinateCamera(azimuth=azimuth, elevation=elevation, theta=theta))
        render_paths = scene.render(dest_path, export_blend_path=cls.export_blend_path)
        return render_paths[0]

    @classmethod
    @notebook_preview
    def render_from_config(cls, config_path, dest_path=None):
        """Render from config file."""
        if dest_path is None:
            dest_path = pathlib.PosixPath(tempfile.gettempdir()) / f'{uuid.uuid4().int}.png'

        scene = Scene.from_config(config_path)
        render_paths = scene.render(dest_path, export_blend_path=cls.export_blend_path)
        return render_paths[0]

    @classmethod
    @notebook_preview
    def gif(cls, mesh_path, dest_path=None, elevation=30, theta=0, frames=60, duration=2, **kwargs):
        """Render a sequence of frames and export as GIF.

        The renderer will make one full loop around the object. The azimuth angles are thus
        dependent on the number of frames.
        """
        if dest_path is None:
            dest_path = pathlib.PosixPath(tempfile.gettempdir()) / f'{uuid.uuid4().int}.gif'

        scene = Scene(**kwargs)
        scene.add_object(Mesh(mesh_path=mesh_path))
        for angle in range(0, 360, int(360 / frames)):
            scene.add_object(SphericalCoordinateCamera(azimuth=angle, elevation=elevation, theta=theta))
        return scene.render_gif(dest_path, duration=duration / frames, export_blend_path=cls.export_blend_path)
