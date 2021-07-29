from blenderless.camera import SphericalCoordinateCamera


def test_spherical_coordinate_camera():
    camera = SphericalCoordinateCamera(azimuth=0, elevation=0, theta=0, distance=1)
    assert camera.xyz == (1, 0, 0)
