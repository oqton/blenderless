import tempfile
import uuid

from blenderless.camera import *
from blenderless.geometry import *
from blenderless.scene import *
from blenderless.utils import notebook_preview


@notebook_preview
def render(mesh_path, dest_path=None, file_name=None, azimuth=45, elevation=30, theta=0, **kwargs):
    if dest_path is None:
        dest_path = tempfile.gettempdir()
    if file_name is None:
        file_name = f'/{uuid.uuid4().int}.png'

    scene = Scene(**kwargs)
    scene.add_object(Mesh(mesh_path=mesh_path))
    scene.add_object(SphericalCoordinateCamera(azimuth=azimuth, elevation=elevation, theta=theta))
    render_paths = scene.render(dest_path)
    return render_paths[0]
