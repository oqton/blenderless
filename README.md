# Blenderless

Blenderless is the Python package for easy headless rendering using Blender.

While Blender is a fantastic open-source 3D modeling software which can be run from the command line, there are still some inconveniences when rendering from a headless server:

 - the blender python interface `bpy` can only be imported a single time,
 - and, there is no framebuffer for blender to write to.

Furthermore, the `bpy` interface has a steep learning curve.

 This package is meant to overcome these issues in a easy-to-use manner. It does so by first defining the entire scene and only interacting with the `bpy` at render time in a separate thread using a virtual framebuffer.

 Example use cases:
  - Generating thumbnails or previews from 3D files.
  - Batch generation of views from 3D files.
  - Automatic generation of compositions of a set of meshes into a single scene
  - Converting meshes and labels into .blend files
  - Export GIF animations of a camera looping around an object.


## How to use this

### Resources:
 - You can find basic examples in the [unit tests](https://github.com/oqton/blenderless/tree/master/tests/test_data).
 - [Notebook examples](https://github.com/oqton/blenderless/tree/master/notebooks) (point clouds, mesh face colors, ...)


### Python module

The blenderless package can be loaded as a module. The main functionality is exposed using the Blenderless class. There is support for Jupyter Notebooks as the images/gifs will be shown as IPython Image objects automatically.


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
$ blenderless image foo.stl output.png
$ blenderless --export-blend-path export.blend image foo.stl output.png # If .blend needs to be exported
```

Render geometry to gif with a camera looping around an object.

```sh
$ blenderless gif foo.stl output.gif
```

The following command rendera a YAML config to an image

```sh
$ blenderless config scene.yml output.png
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


### Export blender file

## Install

```buildoutcfg
sudo apt-get install xvfb
pipx install poetry==1.1.5
make .venv
```

### Testing

```sh
make test
```
