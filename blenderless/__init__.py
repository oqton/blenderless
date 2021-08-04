import pathlib
import tempfile
import uuid

from blenderless.camera import *
from blenderless.geometry import *
from blenderless.material import *
from blenderless.scene import *
from blenderless.utils import notebook_preview


@notebook_preview
def render(mesh_path, dest_path=None, azimuth=45, elevation=30, theta=0, **kwargs):
    if dest_path is None:
        dest_path = pathlib.PosixPath(tempfile.gettempdir()) / f'{uuid.uuid4().int}.png'

    scene = Scene(**kwargs)
    scene.add_object(Mesh(mesh_path=mesh_path))
    scene.add_object(SphericalCoordinateCamera(azimuth=azimuth, elevation=elevation, theta=theta))
    render_paths = scene.render(dest_path)
    return render_paths[0]


@notebook_preview
def gif(mesh_path, dest_path=None, elevation=30, theta=0, frames=60, duration=2, **kwargs):
    if dest_path is None:
        dest_path = pathlib.PosixPath(tempfile.gettempdir()) / f'{uuid.uuid4().int}.gif'

    scene = Scene(**kwargs)
    scene.add_object(Mesh(mesh_path=mesh_path))
    for angle in range(0, 360, int(360 / frames)):
        scene.add_object(SphericalCoordinateCamera(azimuth=angle, elevation=elevation, theta=theta))
    return scene.render_gif(dest_path, duration=duration / frames)
