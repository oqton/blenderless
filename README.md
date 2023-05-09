# Blenderless

Blenderless is the Python package for easy headless rendering using Blender.

While Blender is a fantastic open-source 3D modeling software which can be run from the command line, there are still some inconveniences when rendering from a headless server.
Furthermore, the `bpy` interface has a steep learning curve.
This package is meant to overcome these issues in a easy-to-use manner.

Example use-cases:
  - Generating thumbnails or previews from 3D files.
  - Batch generation of views from 3D files.
  - Automatic generation of compositions of a set of meshes into a single scene
  - Converting meshes and labels into .blend files
  - Export GIF animations of a camera looping around an object.


## How to use this

### Resources:

You can find basic examples in the [unit tests](https://github.com/oqton/blenderless/tree/master/tests/test_data).

### Python module

The blenderless package can be loaded as a module. The main functionality is exposed using the Blenderless class.


```python
from blenderless import Blenderless

# Set the following property if you want to export the generated blender workspace.
Blenderless.export_blend_path = 'export.blend'

# Render single STL file
path_to_foo_png = Blenderless.render('meshpath.stl', dest_path=None, azimuth=45, elevation=30, theta=0)

# Render from config, note that objects and cameras are defined within the YAML config.
path_to_foo_png = Blenderless.render_from_config('config.yml', dest_path=None)

# Render GIF animation, note that azimuth is defined by number of frames.
path_to_foo_gif = Blenderless.gif(cls, mesh_path, dest_path=None, elevation=30, theta=0, frames=60, duration=2)
```

### Command-line interface

Render geometry file to image

```sh
bazel run //blenderless -- image /path/to/foo.stl /path/to/output.png
bazel run //blenderless -- --export-blend-path /path/to/export.blend image /path/to/foo.stl /path/to/output.png # If .blend needs to be exported
```

Render geometry to gif with a camera looping around an object.

```sh
bazel run //blenderless -- gif /path/to/foo.stl /path/to/output.gif
```

The following command rendera a YAML config to an image

```sh
bazel run //blenderless -- config /path/to/scene.yml /path/to/output.png
```

### YAML configuration files

More advanced scenes can be defined using a YAML configuration file. In this file objects, cameras, labels, materials and presets can be defined.

Example:
```yaml
scene: # See options in blenderless.scene.Scene
  preset_path: ../../preset.blend

cameras: # See options in blenderless.camera
  - _target_: blenderless.camera.SphericalCoordinateCamera # Instantiate one camera with following arguments
    azimuth: 45
    elevation: 30
    theta: 0
    distance: 1

objects: # See blenderless.geometry and blenderless.material
  - _target_: blenderless.geometry.Mesh # Refers to classes within the blenderless package
    mesh_path: ../../mesh/3DBenchy.stl # Constructor argument
    material: # Constructor argument pointing towards another class within the blenderless package
      _target_: blenderless.material.MaterialFromName
      material_name: test_material # Link to material name known in present.blend

  - _target_: blenderless.geometry.BlenderLabel
    label_value: '42'
```

## Install

Make sure to have installed a recent Bazel >= 5.2 and Python3.10.
Bazel will internally search for `python3.10` executable.

### Testing

```sh
bazel test //...
```
